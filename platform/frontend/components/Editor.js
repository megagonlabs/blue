import { closeBrackets } from "@codemirror/autocomplete";
import { indentWithTab } from "@codemirror/commands";
import { json, jsonParseLinter } from "@codemirror/lang-json";
import { bracketMatching, indentUnit } from "@codemirror/language";
import { forEachDiagnostic, lintGutter, linter } from "@codemirror/lint";
import { EditorState } from "@codemirror/state";
import { keymap, lineNumbers } from "@codemirror/view";
import { EditorView, minimalSetup } from "codemirror";
import _ from "lodash";
import { useCallback, useEffect, useRef } from "react";
export default function Editor({ code, setCode, setError }) {
    const editor = useRef();
    const debounced = useCallback(
        _.debounce((v) => {
            let error = false;
            forEachDiagnostic(v.state, (diagnostic) => {
                if (_.isEqual(diagnostic.severity, "error")) {
                    error = true;
                }
            });
            setError(error);
            if (!error) {
                setCode(v.state.doc.toString());
            }
        }, 500),
        []
    );
    const onUpdate = EditorView.updateListener.of((v) => {
        debounced(v);
    });
    useEffect(() => {
        const state = EditorState.create({
            doc: code,
            extensions: [
                minimalSetup,
                lineNumbers(),
                bracketMatching(),
                closeBrackets(),
                linter(jsonParseLinter()),
                lintGutter(),
                keymap.of([indentWithTab]),
                indentUnit.of("    "),
                json(),
                onUpdate,
            ],
        });
        const view = new EditorView({
            state,
            parent: editor.current,
        });
        return () => {
            view.destroy();
        };
    }, []);
    return <div ref={editor} />;
}

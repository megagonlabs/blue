import { Classes } from "@blueprintjs/core";
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
export default function Editor({
    code,
    setCode,
    setError,
    setLoading,
    setInitialized,
    initialized,
}) {
    const editor = useRef();
    const debounced = useCallback(
        _.debounce((v, setInitialized) => {
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
            setLoading(false);
            setInitialized(true);
        }, 800),
        []
    );
    const onUpdate = EditorView.updateListener.of((v) => {
        if (v.docChanged) {
            setLoading(true);
        }
        debounced(v, setInitialized);
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
    return (
        <div className={!initialized ? Classes.SKELETON : null} ref={editor} />
    );
}

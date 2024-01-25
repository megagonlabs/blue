import { closeBrackets } from "@codemirror/autocomplete";
import { indentWithTab } from "@codemirror/commands";
import { json, jsonParseLinter } from "@codemirror/lang-json";
import { bracketMatching, indentUnit } from "@codemirror/language";
import { forEachDiagnostic, lintGutter, linter } from "@codemirror/lint";
import { EditorState } from "@codemirror/state";
import { keymap, lineNumbers } from "@codemirror/view";
import { EditorView, minimalSetup } from "codemirror";
import _ from "lodash";
import { useCallback, useEffect, useRef, useState } from "react";
export default function Editor({ code, setCode, setError, setLoading }) {
    const [doc, setDoc] = useState(code);
    useEffect(() => {
        setCode(doc);
    }, [doc]);
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
                setDoc(v.state.doc.toString());
            }
            setLoading(false);
        }, 300),
        []
    );
    const onUpdate = EditorView.updateListener.of((v) => {
        if (v.docChanged) {
            setLoading(true);
        }
        debounced(v);
    });
    useEffect(() => {
        const state = EditorState.create({
            doc: doc,
            extensions: [
                minimalSetup,
                lineNumbers(),
                bracketMatching(),
                closeBrackets(),
                linter(jsonParseLinter(), { delay: 0 }),
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

import { closeBrackets } from "@codemirror/autocomplete";
import { indentWithTab } from "@codemirror/commands";
import { json, jsonParseLinter } from "@codemirror/lang-json";
import { bracketMatching, indentUnit } from "@codemirror/language";
import { forEachDiagnostic, linter } from "@codemirror/lint";
import { EditorState } from "@codemirror/state";
import { keymap, lineNumbers } from "@codemirror/view";
import { EditorView } from "codemirror";
import _ from "lodash";
import { useEffect, useRef } from "react";
export default function Editor({ code, setCode, setError }) {
    const editor = useRef();
    const onUpdate = EditorView.updateListener.of((v) => {
        const diagnostics = new Promise((resolve, reject) => {
            forEachDiagnostic(v.state, (diagnostic) => {
                if (_.isEqual(diagnostic.severity, "error")) {
                    reject();
                }
            });
            resolve();
        });
        diagnostics
            .then(() => {
                setError(false);
                setCode(v.state.doc.toString());
            })
            .catch(() => {
                setError(true);
            });
    });
    useEffect(() => {
        const state = EditorState.create({
            doc: code,
            extensions: [
                lineNumbers(),
                bracketMatching(),
                closeBrackets(),
                linter(jsonParseLinter()),
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

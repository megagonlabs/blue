import { closeBrackets } from "@codemirror/autocomplete";
import { indentWithTab } from "@codemirror/commands";
import { json, jsonParseLinter } from "@codemirror/lang-json";
import { bracketMatching, indentUnit } from "@codemirror/language";
import { forEachDiagnostic, lintGutter, linter } from "@codemirror/lint";
import { EditorState } from "@codemirror/state";
import { keymap, lineNumbers } from "@codemirror/view";
import { EditorView, minimalSetup } from "codemirror";
import { jsonSchema } from "codemirror-json-schema";
import _ from "lodash";
import { useCallback, useEffect, useRef, useState } from "react";
export default function JsonEditor({
    code,
    setCode,
    setError,
    setLoading,
    schema = null,
    allowSaveWithError = false,
}) {
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
            if (_.isFunction(setError)) {
                setError(error);
            }
            if (!error || allowSaveWithError) {
                setDoc(v.state.doc.toString());
            }
            if (_.isFunction(setLoading)) {
                setLoading(false);
            }
        }, 300),
        []
    );
    const onUpdate = EditorView.updateListener.of((v) => {
        if (_.isFunction(setLoading) && v.docChanged) {
            setLoading(true);
        }
        debounced(v);
    });
    const [codeEditorView, setCodeEditorView] = useState(null);
    useEffect(() => {
        if (_.isEqual(code, doc) || _.isNil(codeEditorView)) {
            return;
        }
        codeEditorView.dispatch({
            changes: { from: 0, to: doc.length, insert: code },
        });
    }, [code]);
    useEffect(() => {
        let extensionList = [
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
        ];
        if (!_.isEmpty(schema)) {
            extensionList.push(jsonSchema(schema));
        }
        const state = EditorState.create({
            doc: doc,
            extensions: extensionList,
        });
        const view = new EditorView({
            state,
            parent: editor.current,
        });
        view.contentDOM.addEventListener("blur", () => {
            var editableFix = document.createElement("input");
            editableFix.style =
                "position: absolute; width: 1px; left: 0px; top: 0px;";
            editableFix.tabIndex = -1;
            view.contentDOM.appendChild(editableFix);
            editableFix.focus();
            editableFix.setSelectionRange(0, 0);
            editableFix.blur();
            setTimeout(() => {
                editableFix.remove();
            }, 0);
        });
        setCodeEditorView(view);
        return () => {
            view.destroy();
        };
    }, []);
    return <div ref={editor} />;
}

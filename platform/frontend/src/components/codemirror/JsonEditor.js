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
    schema = null,
    allowEditWithError = false,
    allowPopulateOnce = false,
    alwaysAllowPopulate = false,
}) {
    const prePopulateOnce = useRef(!allowPopulateOnce);
    const [doc, setDoc] = useState(code);
    useEffect(() => {
        setCode(doc);
    }, [doc]);
    const editor = useRef();
    const onUpdate = EditorView.updateListener.of((v) => {
        // v.docChanged
        debounced(v);
    });
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
            if (!error || allowEditWithError) {
                setDoc(v.state.doc.toString());
            }
        }, 300),
        []
    );
    const [codeEditorView, setCodeEditorView] = useState(null);
    useEffect(() => {
        if (
            _.isEqual(code, doc) ||
            _.isNil(codeEditorView) ||
            (prePopulateOnce.current && !alwaysAllowPopulate)
        )
            return;
        prePopulateOnce.current = true;
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
        setCodeEditorView(view);
        return () => {
            view.destroy();
        };
    }, []);
    return <div ref={editor} />;
}

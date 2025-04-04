import { closeBrackets } from "@codemirror/autocomplete";
import { indentWithTab } from "@codemirror/commands";
import { json, jsonParseLinter } from "@codemirror/lang-json";
import { bracketMatching, indentUnit } from "@codemirror/language";
import { forEachDiagnostic, lintGutter, linter } from "@codemirror/lint";
import { Compartment, EditorState } from "@codemirror/state";
import { keymap, lineNumbers } from "@codemirror/view";
import { showMinimap } from "@replit/codemirror-minimap";
import classNames from "classnames";
import { EditorView, minimalSetup } from "codemirror";
import { jsonSchema } from "codemirror-json-schema";
import _ from "lodash";
import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { AuthContext } from "../contexts/auth-context";
export default function JsonEditor({
    code,
    setCode,
    setError,
    schema = null,
    allowEditWithError = false,
    allowPopulateOnce = false,
    alwaysAllowPopulate = false,
    useMinimap = true,
    containOverscrollBehavior = true,
}) {
    const prePopulateOnce = useRef(!allowPopulateOnce);
    const { settings } = useContext(AuthContext);
    const darkMode = _.get(settings, "dark_mode", false);
    const [doc, setDoc] = useState(code);
    useEffect(() => {
        setCode(doc);
    }, [doc]);
    const editor = useRef();
    const themeCompartment = useRef(new Compartment());
    const lightTheme = EditorView.theme({}, { dark: false });
    const darkTheme = EditorView.theme({}, { dark: true });
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
        if (_.isNil(codeEditorView)) return;
        codeEditorView.dispatch({
            effects: themeCompartment.current.reconfigure(
                darkMode ? darkTheme : lightTheme
            ),
        });
    }, [darkMode]);
    useEffect(() => {
        let create = (view) => {
            const dom = document.createElement("div");
            return { dom };
        };
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
            themeCompartment.current.of(darkMode ? darkTheme : lightTheme),
        ];
        if (useMinimap)
            extensionList.push(
                showMinimap.compute(["doc"], (state) => {
                    return {
                        create,
                        displayText: "blocks",
                        showOverlay: "mouse-over",
                    };
                })
            );
        if (!_.isEmpty(schema)) extensionList.push(jsonSchema(schema));
        const state = EditorState.create({
            doc: doc,
            extensions: extensionList,
        });
        const view = new EditorView({ state, parent: editor.current });
        setCodeEditorView(view);
        return () => {
            view.destroy();
        };
    }, []);
    return (
        <div
            className={classNames({
                "full-parent-height": true,
                "cm-overscroll-behavior-contain": containOverscrollBehavior,
            })}
            ref={editor}
        />
    );
}

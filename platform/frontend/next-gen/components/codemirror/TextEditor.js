import { useAppStore } from "@/stores/app-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Colors,
    Intent,
    Size,
} from "@blueprintjs/core";
import { closeBrackets } from "@codemirror/autocomplete";
import { indentWithTab } from "@codemirror/commands";
import { bracketMatching, indentUnit } from "@codemirror/language";
import { forEachDiagnostic, lintGutter } from "@codemirror/lint";
import { Compartment, EditorState } from "@codemirror/state";
import { oneDark } from "@codemirror/theme-one-dark";
import { EditorView, keymap, lineNumbers } from "@codemirror/view";
import { faCheck } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { showMinimap } from "@replit/codemirror-minimap";
import classNames from "classnames";
import { minimalSetup } from "codemirror";
import _, { debounce } from "lodash";
import { useCallback, useEffect, useRef, useState } from "react";
import { FAIcon } from "../FAIcon";
const TAB_INDENT = "    ";
export default function TextEditor({
    textObject,
    loading,
    controlStripProps = {},
    className = [],
    onSave = null,
    setBack = null,
    useMinimap = true,
    breaker = null,
}) {
    const textString = textObject;
    const editor = useRef();
    const [editorView, setEditorView] = useState(null);
    const darkMode = useAppStore((state) => state.dark_mode);
    const [error, setError] = useState(false);
    const [doc, setDoc] = useState(textString);
    useEffect(() => {
        try {
            if (_.isFunction(setBack)) {
                setBack(doc);
            }
        } catch (error) {}
    }, [doc]);
    const themeCompartment = useRef(new Compartment());
    const readOnlyCompartment = useRef(new Compartment());
    const theme = darkMode
        ? EditorView.theme(
              {
                  "&": { height: "100%" },
                  ".cm-gutters": {
                      backgroundColor: Colors.DARK_GRAY1,
                      borderRight: "1px solid rgba(255, 255, 255, 0.2)",
                  },
                  ".cm-minimap-inner": {
                      backgroundColor: Colors.DARK_GRAY1,
                      borderLeft: "1px solid rgba(255, 255, 255, 0.2)",
                  },
                  ".cm-minimap-gutter": { borderRight: 0 },
              },
              oneDark
          )
        : EditorView.theme({
              "&": { height: "100%" },
              ".cm-gutters": {
                  backgroundColor: Colors.LIGHT_GRAY5,
                  borderRight: "1px solid rgba(17, 20, 24, 0.15)",
              },
              ".cm-minimap-inner": {
                  backgroundColor: Colors.LIGHT_GRAY5,
                  borderLeft: "1px solid rgba(17, 20, 24, 0.15)",
              },
              ".cm-minimap-gutter": { borderRight: 0 },
          });
    const onUpdate = EditorView.updateListener.of((v) => {
        // v.docChanged
        debounced(v);
    });
    const debounced = useCallback(
        debounce((v) => {
            let error = false;
            forEachDiagnostic(v.state, (diagnosis) => {
                if (_.isEqual(diagnosis.severity, "error")) {
                    error = true;
                }
            });
            setError(error);
            setDoc(v.state.doc.toString());
        }, 300),
        []
    );
    useEffect(() => {
        if (_.isNull(editorView)) return;
        editorView.dispatch({
            effects: [
                themeCompartment.current.reconfigure(theme),
                readOnlyCompartment.current.reconfigure(
                    EditorState.readOnly.of(loading)
                ),
            ],
        });
    }, [darkMode, loading]);
    const overwrite = (string) => {
        if (_.isNull(editorView)) return;
        editorView.dispatch({
            changes: {
                from: 0,
                to: _.size(editorView.state.doc),
                insert: string,
            },
        });
    };
    useEffect(() => {
        try {
            // if breaker is set to false, trigger forced update
            // or the object being edited is out of sync with doc
            if (
                (!_.isNull(breaker) && !breaker.current) ||
                !_.isEqual(textObject, doc)
            ) {
                if (!_.isNull(breaker)) {
                    breaker.current = true;
                }
                overwrite(textString);
            }
        } catch (error) {}
    }, [textObject]);
    useEffect(() => {
        let create = (view) => {
            const dom = document.createElement("div");
            return { dom };
        };
        let extensions = [
            minimalSetup,
            lineNumbers(),
            bracketMatching(),
            closeBrackets(),
            lintGutter(),
            keymap.of([indentWithTab]),
            indentUnit.of(TAB_INDENT),
            onUpdate,
            themeCompartment.current.of(theme),
            readOnlyCompartment.current.of(EditorState.readOnly.of(false)),
        ];
        if (useMinimap) {
            extensions.push(
                showMinimap.compute(["doc"], (state) => {
                    return {
                        create,
                        displayText: "blocks",
                        showOverlay: "mouse-over",
                    };
                })
            );
        }
        const state = EditorState.create({ doc, extensions });
        const view = new EditorView({ state, parent: editor.current });
        setEditorView(view);
        return () => {
            view.destroy();
        };
    }, []);
    const elementRef = useRef(null);
    const controlStripSize = _.get(controlStripProps, "size", null);
    const showControlStrip = _.isFunction(onSave);
    return (
        <div className={classNames(className, "full-parent-dimension")}>
            {showControlStrip && (
                <div
                    ref={elementRef}
                    className="border-bottom"
                    style={{
                        display: "flex",
                        padding: 10,
                        alignItems: "center",
                        justifyContent: "space-between",
                    }}
                >
                    <ButtonGroup
                        size={controlStripSize}
                        variant={ButtonVariant.MINIMAL}
                    >
                        {_.isFunction(onSave) && (
                            <Button
                                loading={loading}
                                disabled={error}
                                icon={<FAIcon icon={faCheck} />}
                                intent={Intent.SUCCESS}
                                text="Save"
                                onClick={() => {
                                    onSave(doc);
                                }}
                            />
                        )}
                    </ButtonGroup>
                </div>
            )}
            <div
                style={{
                    height: `calc(100% - ${
                        showControlStrip
                            ? _.isEqual(controlStripSize, Size.LARGE)
                                ? 61
                                : 51
                            : 0
                    }px)`,
                }}
            >
                <div className="full-parent-height" ref={editor} />
            </div>
        </div>
    );
}

import EditorJSON from "@/components/codemirror/EditorJSON";
import {
    DATA_JSON_SCHEMA,
    UI_JSON_SCHEMA,
} from "@/components/codemirror/constant";
import { JSONFORMS_RENDERERS } from "@/components/constant";
import { faIcon } from "@/components/icon";
import DocDrawer from "@/components/jsonforms/docs/DocDrawer";
import {
    Alignment,
    Button,
    ButtonGroup,
    Callout,
    Card,
    Classes,
    Divider,
    Intent,
    NonIdealState,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowsFromLine,
    faBookOpenCover,
    faBracketsCurly,
    faCircleXmark,
    faIndent,
    faRotate,
    faTrash,
} from "@fortawesome/pro-duotone-svg-icons";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells } from "@jsonforms/vanilla-renderers";
import { Allotment } from "allotment";
import classNames from "classnames";
import _ from "lodash";
import { createRef, useEffect, useState } from "react";
import { useErrorBoundary, withErrorBoundary } from "react-use-error-boundary";
const DEFAULT_SCHEMA = JSON.stringify(
    { type: "object", properties: {} },
    null,
    4
);
function Designer() {
    const [error, resetError] = useErrorBoundary();
    const topPaneRef = createRef();
    const [uiSchema, setUiSchema] = useState({});
    const [schema, setSchema] = useState({});
    const [data, setData] = useState({});
    const [jsonUiSchema, setJsonUiSchema] = useState("{}");
    const [jsonSchema, setJsonSchema] = useState(DEFAULT_SCHEMA);
    const [uiSchemaError, setUiSchemaError] = useState(false);
    const [schemaError, setSchemaError] = useState(false);
    const [uiSchemaLoading, setUiSchemaLoading] = useState(true);
    const [uiSchemaInitialized, setUiSchemaInitialized] = useState(false);
    const [schemaLoading, setSchemaLoading] = useState(true);
    const [schemaInitialized, setSchemaInitialized] = useState(false);
    useEffect(() => {
        if (error) {
            setIsDocOpen(false);
        }
    }, [error]);
    useEffect(() => {
        if (!uiSchemaLoading) {
            let uiSchemaCache = sessionStorage.getItem("jsonUiSchema");
            if (!uiSchemaInitialized && uiSchemaCache) {
                setJsonUiSchema(uiSchemaCache);
            }
            setUiSchemaInitialized(true);
        }
    }, [uiSchemaLoading]); // eslint-disable-line react-hooks/exhaustive-deps
    useEffect(() => {
        if (!schemaLoading) {
            let schemaCache = sessionStorage.getItem("jsonSchema");
            if (!schemaInitialized && schemaCache) {
                setJsonSchema(schemaCache);
            }
            setSchemaInitialized(true);
        }
    }, [schemaLoading]); // eslint-disable-line react-hooks/exhaustive-deps
    useEffect(() => {
        try {
            setUiSchema(JSON.parse(jsonUiSchema));
        } catch (error) {}
        if (uiSchemaInitialized) {
            sessionStorage.setItem("jsonUiSchema", jsonUiSchema);
        }
    }, [jsonUiSchema]); // eslint-disable-line react-hooks/exhaustive-deps
    useEffect(() => {
        try {
            setSchema(JSON.parse(jsonSchema));
        } catch (error) {}
        if (schemaInitialized) {
            sessionStorage.setItem("jsonSchema", jsonSchema);
        }
    }, [jsonSchema]); // eslint-disable-line react-hooks/exhaustive-deps
    const BUTTON_PROPS = {
        large: true,
        alignText: Alignment.LEFT,
        fill: true,
        minimal: true,
        style: { fontWeight: 600 },
    };
    const handleFormattingCode = () => {};
    const handleReset = () => {
        topPaneRef.current.resize([50, 50]);
        setUiSchemaError(false);
        setSchemaError(false);
        setUiSchema("{}");
        setSchema(DEFAULT_SCHEMA);
        sessionStorage.removeItem("jsonUiSchema");
        sessionStorage.removeItem("jsonSchema");
    };
    const [isDocOpen, setIsDocOpen] = useState(
        _.isEqual(sessionStorage.getItem("isDocOpen"), "true")
    );
    return (
        <>
            <DocDrawer isOpen={isDocOpen} setIsDocOpen={setIsDocOpen} />
            <Card interactive style={{ padding: 5, borderRadius: 0 }}>
                <ButtonGroup large minimal>
                    {error ? (
                        <>
                            <Button
                                intent={Intent.SUCCESS}
                                text="Re-run"
                                onClick={resetError}
                                icon={faIcon({ icon: faRotate })}
                            />
                            <Divider />
                        </>
                    ) : null}
                    <Tooltip
                        placement="bottom-start"
                        minimal
                        content="Format Code"
                    >
                        <Button
                            icon={faIcon({ icon: faIndent })}
                            onClick={handleFormattingCode}
                        />
                    </Tooltip>
                    <Button
                        text="Docs."
                        active={isDocOpen}
                        icon={faIcon({ icon: faBookOpenCover })}
                        onClick={() => {
                            setIsDocOpen(!isDocOpen);
                            sessionStorage.setItem(
                                "isDocOpen",
                                String(!isDocOpen)
                            );
                        }}
                    />
                    <Divider />
                    <Button
                        intent={Intent.DANGER}
                        text="Clear All"
                        onClick={handleReset}
                        icon={faIcon({ icon: faTrash })}
                    />
                </ButtonGroup>
            </Card>
            <div style={{ height: "calc(100% - 50px)" }}>
                <Allotment>
                    <Allotment.Pane minSize={321.094}>
                        <Allotment vertical ref={topPaneRef}>
                            <Allotment.Pane minSize={187.5}>
                                <div
                                    style={{
                                        padding: 5,
                                        borderBottom:
                                            "1px solid rgba(17, 20, 24, 0.15)",
                                    }}
                                >
                                    <Tooltip
                                        fill
                                        minimal
                                        placement="bottom-start"
                                        content={
                                            "The UI schema that describes how the form should be rendered."
                                        }
                                    >
                                        <Button
                                            intent={
                                                uiSchemaError
                                                    ? Intent.DANGER
                                                    : null
                                            }
                                            icon={
                                                uiSchemaError
                                                    ? faIcon({
                                                          icon: faCircleXmark,
                                                      })
                                                    : null
                                            }
                                            {...BUTTON_PROPS}
                                            text="UI Schema"
                                            onClick={() => {
                                                topPaneRef.current.resize([
                                                    window.innerHeight,
                                                    187.5,
                                                ]);
                                            }}
                                            rightIcon={faIcon({
                                                icon: faArrowsFromLine,
                                            })}
                                        />
                                    </Tooltip>
                                </div>
                                <div
                                    className={classNames({
                                        "full-parent-height": true,
                                        [Classes.SKELETON]:
                                            uiSchemaLoading &&
                                            !uiSchemaInitialized,
                                    })}
                                    style={{
                                        overflowY: "auto",
                                        maxHeight: "calc(100% - 51px)",
                                    }}
                                >
                                    <EditorJSON
                                        schema={UI_JSON_SCHEMA}
                                        setLoading={setUiSchemaLoading}
                                        allowSaveWithError
                                        code={jsonUiSchema}
                                        setCode={setJsonUiSchema}
                                        setError={setUiSchemaError}
                                    />
                                </div>
                            </Allotment.Pane>
                            <Allotment.Pane minSize={187.5}>
                                <div
                                    style={{
                                        padding: 5,
                                        borderBottom:
                                            "1px solid rgba(17, 20, 24, 0.15)",
                                    }}
                                >
                                    <Tooltip
                                        fill
                                        minimal
                                        placement="bottom-start"
                                        content={
                                            "The JSON schema that describes the underlying data."
                                        }
                                    >
                                        <Button
                                            intent={
                                                schemaError
                                                    ? Intent.DANGER
                                                    : null
                                            }
                                            icon={
                                                schemaError
                                                    ? faIcon({
                                                          icon: faCircleXmark,
                                                      })
                                                    : null
                                            }
                                            {...BUTTON_PROPS}
                                            text="Schema"
                                            onClick={() => {
                                                topPaneRef.current.resize([
                                                    187.5,
                                                    window.innerHeight,
                                                ]);
                                            }}
                                            rightIcon={faIcon({
                                                icon: faArrowsFromLine,
                                            })}
                                        />
                                    </Tooltip>
                                </div>
                                <div
                                    className={classNames({
                                        "full-parent-height": true,
                                        [Classes.SKELETON]:
                                            schemaLoading && !schemaInitialized,
                                    })}
                                    style={{
                                        overflowY: "auto",
                                        maxHeight: "calc(100% - 51px)",
                                    }}
                                >
                                    <EditorJSON
                                        schema={DATA_JSON_SCHEMA}
                                        setLoading={setSchemaLoading}
                                        allowSaveWithError
                                        code={jsonSchema}
                                        setCode={setJsonSchema}
                                        setError={setSchemaError}
                                    />
                                </div>
                            </Allotment.Pane>
                        </Allotment>
                    </Allotment.Pane>
                    <Allotment.Pane minSize={400}>
                        <div
                            className="full-parent-height"
                            style={{ padding: 20, overflowY: "auto" }}
                        >
                            {!_.isEmpty(uiSchema) ? (
                                <Callout
                                    icon={null}
                                    intent={error ? Intent.DANGER : null}
                                    style={{
                                        maxWidth: "min(802.2px, 100%)",
                                        whiteSpace: "pre-wrap",
                                        width: "fit-content",
                                    }}
                                >
                                    {!error ? (
                                        <JsonForms
                                            schema={schema}
                                            uischema={uiSchema}
                                            data={data}
                                            renderers={JSONFORMS_RENDERERS}
                                            cells={vanillaCells}
                                            onChange={({ data, errors }) => {
                                                console.log(data, errors);
                                                setData(data);
                                            }}
                                        />
                                    ) : (
                                        String(error)
                                    )}
                                </Callout>
                            ) : (
                                <NonIdealState
                                    icon={faIcon({
                                        icon: faBracketsCurly,
                                        size: 50,
                                    })}
                                    title="Empty UI Schema"
                                />
                            )}
                        </div>
                    </Allotment.Pane>
                </Allotment>
            </div>
        </>
    );
}
export default withErrorBoundary(Designer);

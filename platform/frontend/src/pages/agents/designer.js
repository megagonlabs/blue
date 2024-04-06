import Editor from "@/components/Editor";
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
} from "@blueprintjs/core";
import {
    faArrowsFromLine,
    faBookOpenCover,
    faBracketsCurly,
    faCircleXmark,
    faTrash,
} from "@fortawesome/pro-duotone-svg-icons";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells } from "@jsonforms/vanilla-renderers";
import { Allotment } from "allotment";
import classNames from "classnames";
import _ from "lodash";
import { createRef, useEffect, useState } from "react";
export default function Designer() {
    const topPaneRef = createRef();
    const [uiSchema, setUiSchema] = useState("{}");
    const [schema, setSchema] = useState("{}");
    const [data, setData] = useState({});
    const [jsonUiSchema, setJsonUiSchema] = useState({});
    const [jsonSchema, setJsonSchema] = useState({});
    const [uiSchemaError, setUiSchemaError] = useState(false);
    const [schemaError, setSchemaError] = useState(false);
    const [uiSchemaLoading, setUiSchemaLoading] = useState(true);
    const [uiSchemaInitialized, setUiSchemaInitialized] = useState(false);
    const [schemaLoading, setSchemaLoading] = useState(true);
    const [schemaInitialized, setSchemaInitialized] = useState(false);
    useEffect(() => {
        if (!uiSchemaLoading) {
            let uiSchemaCache = sessionStorage.getItem("uiSchema");
            if (!uiSchemaInitialized && uiSchemaCache) {
                setUiSchema(uiSchemaCache);
            }
            setUiSchemaInitialized(true);
        }
    }, [uiSchemaLoading]);
    useEffect(() => {
        if (!schemaLoading) {
            let schemaCache = sessionStorage.getItem("schema");
            if (!schemaInitialized && schemaCache) {
                setSchema(schemaCache);
            }
            setSchemaInitialized(true);
        }
    }, [schemaLoading]);
    useEffect(() => {
        try {
            setJsonUiSchema(JSON.parse(uiSchema));
        } catch (error) {}
        if (uiSchemaInitialized) {
            sessionStorage.setItem("uiSchema", uiSchema);
        }
    }, [uiSchema]);
    useEffect(() => {
        try {
            setJsonSchema(JSON.parse(schema));
        } catch (error) {}
        if (schemaInitialized) {
            sessionStorage.setItem("schema", schema);
        }
    }, [schema]);
    const BUTTON_PROPS = {
        large: true,
        alignText: Alignment.LEFT,
        fill: true,
        minimal: true,
        style: { fontWeight: 600 },
    };
    const handleReset = () => {
        topPaneRef.current.resize([50, 50]);
        setUiSchemaError(false);
        setSchemaError(false);
        setUiSchema("{}");
        setSchema("{}");
        sessionStorage.removeItem("jsonUiSchema");
        sessionStorage.removeItem("jsonSchema");
    };
    const [isDocOpen, setIsDocOpen] = useState(true);
    return (
        <>
            <DocDrawer isOpen={isDocOpen} setIsDocOpen={setIsDocOpen} />
            <Card interactive style={{ padding: 5, borderRadius: 0 }}>
                <ButtonGroup large minimal>
                    <Button
                        text="Docs."
                        icon={faIcon({ icon: faBookOpenCover })}
                        onClick={() => {
                            setIsDocOpen(!isDocOpen);
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
                                    <Button
                                        intent={
                                            uiSchemaError ? Intent.DANGER : null
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
                                    <Editor
                                        setLoading={setUiSchemaLoading}
                                        allowSaveWithError
                                        code={uiSchema}
                                        setCode={setUiSchema}
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
                                    <Button
                                        intent={
                                            schemaError ? Intent.DANGER : null
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
                                    <Editor
                                        setLoading={setSchemaLoading}
                                        allowSaveWithError
                                        code={schema}
                                        setCode={setSchema}
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
                            {!_.isEmpty(jsonUiSchema) ? (
                                <Callout
                                    style={{
                                        maxWidth: "min(802.2px, 100%)",
                                        whiteSpace: "pre-wrap",
                                        width: "fit-content",
                                    }}
                                >
                                    <JsonForms
                                        schema={jsonSchema}
                                        uischema={jsonUiSchema}
                                        data={data}
                                        renderers={JSONFORMS_RENDERERS}
                                        cells={vanillaCells}
                                        onChange={({ data, errors }) => {
                                            console.log(data, errors);
                                            setData(data);
                                        }}
                                    />
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

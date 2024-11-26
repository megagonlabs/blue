import JsonEditor from "@/components/codemirror/JsonEditor";
import {
    DATA_JSON_SCHEMA,
    UI_JSON_SCHEMA,
} from "@/components/codemirror/constant";
import { JSONFORMS_RENDERERS, MIN_ALLOTMENT_PANE } from "@/components/constant";
import { safeJsonParse } from "@/components/helper";
import { faIcon } from "@/components/icon";
import DocDrawer from "@/components/jsonforms/docs/DocDrawer";
import { AppToaster } from "@/components/toaster";
import {
    Alignment,
    Button,
    ButtonGroup,
    Callout,
    Card,
    Checkbox,
    Classes,
    Divider,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    NonIdealState,
    Popover,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowsFromLine,
    faBinaryCircleCheck,
    faBinarySlash,
    faBookOpenCover,
    faBracketsCurly,
    faCircleXmark,
    faClipboard,
    faDownload,
    faIndent,
    faPlay,
    faTrash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells } from "@jsonforms/vanilla-renderers";
import { Allotment } from "allotment";
import classNames from "classnames";
import copy from "copy-to-clipboard";
import jsonFormatter from "json-string-formatter";
import _ from "lodash";
import { createRef, useEffect, useState } from "react";
import { useErrorBoundary, withErrorBoundary } from "react-use-error-boundary";
const DEFAULT_SCHEMA = JSON.stringify(
    { type: "object", properties: {} },
    null,
    4
);
const DEFAULT_UI_SCHEMA = JSON.stringify(
    {
        type: "VerticalLayout",
        elements: [],
    },
    null,
    4
);
function FormDesigner() {
    const [error, resetError] = useErrorBoundary();
    const leftPaneRef = createRef();
    const [uischema, setUischema] = useState({});
    const [schema, setSchema] = useState({});
    const ssData = sessionStorage.getItem("data");
    const [data, setData] = useState(
        _.isNil(ssData) ? {} : safeJsonParse(ssData)
    );
    const [jsonData, setJsonData] = useState(ssData);
    const [jsonUischema, setJsonUischema] = useState(DEFAULT_UI_SCHEMA);
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
            sessionStorage.setItem("isDocOpen", "false");
        }
    }, [error]);
    useEffect(() => {
        let uiSchemaCache = sessionStorage.getItem("jsonUischema");
        if (!uiSchemaInitialized && uiSchemaCache) {
            setJsonUischema(uiSchemaCache);
        }
        setUiSchemaInitialized(true);
        setUiSchemaLoading(false);
        let schemaCache = sessionStorage.getItem("jsonSchema");
        if (!schemaInitialized && schemaCache) {
            setJsonSchema(schemaCache);
        }
        setSchemaInitialized(true);
        setSchemaLoading(false);
    }, []);
    useEffect(() => {
        try {
            setData(JSON.parse(jsonData));
        } catch (error) {}
        sessionStorage.setItem("data", jsonData);
    }, [jsonData]);
    useEffect(() => {
        if (!_.isEqual(data, JSON.parse(jsonData)))
            setJsonData(JSON.stringify(data, null, 4));
    }, [data]);
    useEffect(() => {
        try {
            setUischema(JSON.parse(jsonUischema));
        } catch (error) {}
        if (uiSchemaInitialized) {
            sessionStorage.setItem("jsonUischema", jsonUischema);
        }
    }, [jsonUischema]);
    useEffect(() => {
        try {
            setSchema(JSON.parse(jsonSchema));
            setData({});
        } catch (error) {}
        if (schemaInitialized) {
            sessionStorage.setItem("jsonSchema", jsonSchema);
        }
    }, [jsonSchema]);
    const [resultPanel, setResultPanel] = useState(true);
    const BUTTON_PROPS = {
        large: true,
        alignText: Alignment.LEFT,
        fill: true,
        minimal: true,
        style: { fontWeight: 600 },
    };
    const handleFormattingCode = () => {
        try {
            if (_.isEqual(jsonUischema.replace(/\s/g, ""), "{}")) {
                setJsonUischema("{}");
            } else {
                setJsonUischema(jsonFormatter.format(jsonUischema, "    "));
            }
        } catch (error) {}
        try {
            if (_.isEqual(jsonSchema.replace(/\s/g, ""), "{}")) {
                setJsonSchema("{}");
            } else {
                setJsonSchema(jsonFormatter.format(jsonSchema, "    "));
            }
        } catch (error) {}
        try {
            if (_.isEqual(jsonData.replace(/\s/g, ""), "{}")) {
                setJsonData("{}");
            } else {
                setJsonData(jsonFormatter.format(jsonData, "    "));
            }
        } catch (error) {
            console.log(error);
        }
    };
    const handleExportConfig = (withData) => {
        let result = { schema: schema, uischema: uischema };
        if (withData) {
            _.set(result, "data", data);
        }
        copy(JSON.stringify(result));
        AppToaster.show({
            icon: faIcon({ icon: faClipboard }),
            message: `Copied interactive message configuration (with${
                withData ? "" : "out"
            } default data)`,
        });
    };
    const handleReset = () => {
        leftPaneRef.current.resize([50, 50]);
        setUiSchemaError(false);
        setSchemaError(false);
        setJsonUischema(DEFAULT_UI_SCHEMA);
        setJsonSchema(DEFAULT_SCHEMA);
        setResultPanel(true);
        sessionStorage.removeItem("jsonUischema");
        sessionStorage.removeItem("jsonSchema");
    };
    const [isDocOpen, setIsDocOpen] = useState(
        _.isEqual(sessionStorage.getItem("isDocOpen"), "true")
    );
    return (
        <>
            <DocDrawer
                setJsonUischema={setJsonUischema}
                setJsonData={setJsonData}
                setJsonSchema={setJsonSchema}
                isOpen={isDocOpen}
                setIsDocOpen={setIsDocOpen}
            />
            <Card interactive style={{ padding: 5, borderRadius: 0 }}>
                <ButtonGroup large minimal>
                    <Tooltip
                        usePortal={false}
                        placement="bottom-start"
                        minimal
                        content="Re-run"
                    >
                        <Button
                            disabled={!error}
                            intent={Intent.SUCCESS}
                            onClick={resetError}
                            icon={faIcon({ icon: faPlay })}
                        />
                    </Tooltip>
                    <Tooltip
                        usePortal={false}
                        placement="bottom"
                        minimal
                        content="Format"
                    >
                        <Button
                            icon={faIcon({ icon: faIndent })}
                            onClick={handleFormattingCode}
                        />
                    </Tooltip>
                    <Popover
                        usePortal={false}
                        minimal
                        placement="bottom"
                        content={
                            <Menu>
                                <MenuDivider title="Export" />
                                <MenuItem
                                    icon={faIcon({ icon: faBinaryCircleCheck })}
                                    text="With default data"
                                    onClick={() => {
                                        handleExportConfig(true);
                                    }}
                                />
                                <MenuItem
                                    icon={faIcon({ icon: faBinarySlash })}
                                    text="Without default data"
                                    onClick={() => {
                                        handleExportConfig(false);
                                    }}
                                />
                            </Menu>
                        }
                    >
                        <Tooltip
                            usePortal={false}
                            placement="bottom"
                            minimal
                            content="Export"
                        >
                            <Button icon={faIcon({ icon: faDownload })} />
                        </Tooltip>
                    </Popover>
                    <Divider />
                    <Button
                        intent={Intent.PRIMARY}
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
                        text="Reset all"
                        onClick={handleReset}
                        icon={faIcon({ icon: faTrash })}
                    />
                </ButtonGroup>
            </Card>
            <div style={{ height: "calc(100% - 50px)" }}>
                <Allotment>
                    <Allotment.Pane minSize={MIN_ALLOTMENT_PANE}>
                        <Allotment vertical ref={leftPaneRef}>
                            <Allotment.Pane minSize={187.5}>
                                <div
                                    className="border-bottom"
                                    style={{ padding: 5 }}
                                >
                                    <Tooltip
                                        usePortal={false}
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
                                                          className: "fa-fade",
                                                      })
                                                    : null
                                            }
                                            {...BUTTON_PROPS}
                                            text="UI Schema"
                                            onClick={() => {
                                                leftPaneRef.current.resize([
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
                                    <JsonEditor
                                        schema={UI_JSON_SCHEMA}
                                        allowEditWithError
                                        code={jsonUischema}
                                        alwaysAllowPopulate
                                        setCode={setJsonUischema}
                                        setError={setUiSchemaError}
                                    />
                                </div>
                            </Allotment.Pane>
                            <Allotment.Pane minSize={187.5}>
                                <div
                                    className="border-bottom"
                                    style={{ padding: 5 }}
                                >
                                    <Tooltip
                                        usePortal={false}
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
                                                          className: "fa-fade",
                                                      })
                                                    : null
                                            }
                                            {...BUTTON_PROPS}
                                            text="Data Schema"
                                            onClick={() => {
                                                leftPaneRef.current.resize([
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
                                    <JsonEditor
                                        schema={DATA_JSON_SCHEMA}
                                        allowEditWithError
                                        code={jsonSchema}
                                        alwaysAllowPopulate
                                        setCode={setJsonSchema}
                                        setError={setSchemaError}
                                    />
                                </div>
                            </Allotment.Pane>
                        </Allotment>
                    </Allotment.Pane>
                    <Allotment.Pane minSize={400}>
                        <div
                            className="border-bottom"
                            style={{
                                padding: 5,
                                display: "flex",
                                alignItems: "center",
                            }}
                        >
                            <Button
                                {...BUTTON_PROPS}
                                style={{
                                    pointerEvents: "none",
                                    fontWeight: 600,
                                }}
                                fill={false}
                                text="Result"
                            />
                            <Checkbox
                                className="margin-0 no-text-selection"
                                large
                                label="Show Data"
                                checked={!resultPanel}
                                onChange={(event) =>
                                    setResultPanel(!event.target.checked)
                                }
                            />
                        </div>
                        <div
                            className="full-parent-height"
                            style={{
                                padding: 20,
                                overflowY: "auto",
                                height: "calc(100% - 51px)",
                            }}
                        >
                            <Card
                                style={{
                                    overflow: "hidden",
                                    marginBottom: 20,
                                    padding: 0,
                                    display: resultPanel ? "none" : null,
                                    height: 200,
                                }}
                            >
                                <JsonEditor
                                    allowEditWithError
                                    code={jsonData}
                                    alwaysAllowPopulate
                                    setCode={setJsonData}
                                />
                            </Card>
                            {!_.isEmpty(uischema) ? (
                                <Callout
                                    icon={null}
                                    intent={error ? Intent.DANGER : null}
                                    style={{
                                        maxWidth: "100%",
                                        width: "fit-content",
                                    }}
                                >
                                    <div
                                        style={{
                                            maxWidth: "100%",
                                            minWidth: 50,
                                            whiteSpace: "pre-wrap",
                                            wordBreak: "break-word",
                                            width: "fit-content",
                                            minHeight: 21,
                                            overflow: "hidden",
                                            padding: 1,
                                        }}
                                    >
                                        {!error ? (
                                            <JsonForms
                                                schema={schema}
                                                uischema={uischema}
                                                data={data}
                                                renderers={JSONFORMS_RENDERERS}
                                                cells={vanillaCells}
                                                onChange={({
                                                    data,
                                                    errors,
                                                }) => {
                                                    console.log(data, errors);
                                                    setData(data);
                                                }}
                                            />
                                        ) : (
                                            <>
                                                <div>{String(error)}</div>
                                                <Tag
                                                    large
                                                    minimal
                                                    style={{ marginTop: 5 }}
                                                >
                                                    Click
                                                    {faIcon({
                                                        icon: faPlay,
                                                        style: {
                                                            color: "#1c6e42",
                                                            marginLeft: 5,
                                                            marginRight: 5,
                                                        },
                                                    })}
                                                    to re-run
                                                </Tag>
                                            </>
                                        )}
                                    </div>
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
export default withErrorBoundary(FormDesigner);

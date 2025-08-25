import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Callout,
    Checkbox,
    Colors,
    Divider,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    Popover,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowsFromDottedLine,
    faBinaryCircleCheck,
    faBinarySlash,
    faBookOpenCover,
    faBrowsers,
    faClipboard,
    faDownload,
    faPlay,
    faTrash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells } from "@jsonforms/vanilla-renderers";
import { Allotment } from "allotment";
import copy from "copy-to-clipboard";
import _, { clone } from "lodash";
import { createRef, useEffect, useRef, useState } from "react";
import { useErrorBoundary, withErrorBoundary } from "react-use-error-boundary";
import { v4 as uuidv4 } from "uuid";
import JSONEditor from "../codemirror/JSONEditor";
import {
    MIN_ALLOTMENT_PANE_SIZE,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "../constants";
import { useToaster } from "../contexts/ToasterContext";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import DocContainer from "../jsonforms/docs/DocContainer";
import { JSONFORMS_RENDERERS } from "../jsonforms/renderers";
const DEFAULT_UI_SCHEMA = { type: "VerticalLayout", elements: [] };
const DEFAULT_SCHEMA = { type: "object", properties: {} };
const PANE_BUTTON_PROPS = {
    alignText: Alignment.START,
    fill: true,
    variant: ButtonVariant.MINIMAL,
    style: { fontWeight: 600 },
};
function FormDesigner({ width, height }) {
    const addContainer = useGridStore((state) => state.addContainer);
    const darkMode = useAppStore((state) => state.dark_mode);
    const idRef = useRef(null);
    const [error, resetError] = useErrorBoundary();
    const leftPaneRef = createRef();
    const [uischema, setUischema] = useState(clone(DEFAULT_UI_SCHEMA));
    const [schema, setSchema] = useState(clone(DEFAULT_SCHEMA));
    const [data, setData] = useState({});
    const [showData, setShowData] = useState(false);
    const breaker = useRef(true);
    const { appToaster } = useToaster();
    const handleExport = (withData) => {
        let result = { schema: schema, uischema: uischema };
        if (withData) {
            _.set(result, "data", data);
        }
        copy(JSON.stringify(result));
        appToaster.show({
            icon: <FAIcon icon={faClipboard} />,
            message: `Copied schemas (with${withData ? "" : "out"}  data)`,
        });
    };
    useEffect(() => {
        if (!idRef.current) {
            idRef.current = uuidv4();
        }
    }, []);
    const elementRef = useRef(null);
    return (
        <div ref={elementRef} style={{ width, height }}>
            <div className="border-bottom" style={{ padding: 10 }}>
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    <Tooltip placement="bottom-start" content="Re-run">
                        <Button
                            disabled={!error}
                            intent={Intent.SUCCESS}
                            onClick={resetError}
                            icon={<FAIcon icon={faPlay} />}
                        />
                    </Tooltip>
                    <Popover
                        {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                        boundary={elementRef.current}
                        minimal
                        content={
                            <Menu size={Size.LARGE}>
                                <MenuDivider title="Export" />
                                <MenuItem
                                    icon={<FAIcon icon={faBinaryCircleCheck} />}
                                    text="With data"
                                    onClick={() => {
                                        handleExport(true);
                                    }}
                                />
                                <MenuItem
                                    icon={<FAIcon icon={faBinarySlash} />}
                                    text="Without data"
                                    onClick={() => {
                                        handleExport(false);
                                    }}
                                />
                            </Menu>
                        }
                    >
                        <Tooltip placement="bottom" content="Export">
                            <Button icon={<FAIcon icon={faDownload} />} />
                        </Tooltip>
                    </Popover>
                    <Divider />
                    <Button
                        intent={Intent.PRIMARY}
                        endIcon={<FAIcon icon={faBrowsers} />}
                        icon={<FAIcon icon={faBookOpenCover} />}
                        text="Docs."
                        onClick={() =>
                            addContainer({
                                title: "Form Documentation",
                                icon: faBookOpenCover,
                                content: <DocContainer />,
                            })
                        }
                    />
                    <Divider />
                    <Button
                        intent={Intent.DANGER}
                        icon={<FAIcon icon={faTrash} />}
                        text="Reset all"
                        onClick={() => {
                            breaker.current = false;
                            setData({});
                            setSchema(clone(DEFAULT_SCHEMA));
                            setUischema(clone(DEFAULT_UI_SCHEMA));
                        }}
                    />
                </ButtonGroup>
            </div>
            <div
                className="full-parent-height"
                style={{ maxHeight: "calc(100% - 61px)" }}
            >
                <Allotment>
                    <Allotment.Pane minSize={MIN_ALLOTMENT_PANE_SIZE}>
                        <Allotment vertical ref={leftPaneRef}>
                            <Allotment.Pane minSize={200}>
                                <div
                                    className="border-bottom"
                                    style={{ padding: 10 }}
                                >
                                    <Button
                                        {...PANE_BUTTON_PROPS}
                                        endIcon={
                                            <FAIcon
                                                icon={faArrowsFromDottedLine}
                                            />
                                        }
                                        text="UI Schema"
                                    />
                                </div>
                                <div
                                    className="full-parent-height"
                                    style={{ maxHeight: "calc(100% - 51px)" }}
                                >
                                    <JSONEditor
                                        breaker={breaker}
                                        jsonObject={uischema}
                                        setBack={(object) => {
                                            setUischema(object);
                                        }}
                                    />
                                </div>
                            </Allotment.Pane>
                            <Allotment.Pane minSize={200}>
                                <div
                                    className="border-bottom"
                                    style={{ padding: 10 }}
                                >
                                    <Button
                                        {...PANE_BUTTON_PROPS}
                                        endIcon={
                                            <FAIcon
                                                icon={faArrowsFromDottedLine}
                                            />
                                        }
                                        text="Data Schema"
                                    />
                                </div>
                                <div
                                    className="full-parent-height"
                                    style={{ maxHeight: "calc(100% - 51px)" }}
                                >
                                    <JSONEditor
                                        breaker={breaker}
                                        jsonObject={schema}
                                        setBack={(object) => {
                                            setSchema(object);
                                        }}
                                    />
                                </div>
                            </Allotment.Pane>
                        </Allotment>
                    </Allotment.Pane>
                    <Allotment.Pane minSize={MIN_ALLOTMENT_PANE_SIZE}>
                        <div
                            className="border-bottom"
                            style={{
                                padding: 10,
                                display: "flex",
                                alignItems: "center",
                                gap: 10,
                            }}
                        >
                            <Button
                                {...PANE_BUTTON_PROPS}
                                style={{
                                    pointerEvents: "none",
                                    fontWeight: 600,
                                }}
                                fill={false}
                                text="Result"
                            />
                            <Checkbox
                                checked={showData}
                                onChange={(event) =>
                                    setShowData(event.target.checked)
                                }
                                size={Size.LARGE}
                                className="margin-0 user-selection-none"
                                label="Show data"
                            />
                        </div>
                        <div
                            className="full-parent-dimension"
                            style={{
                                maxHeight: "calc(100% - 51px)",
                                backgroundColor: darkMode ? Colors.BLACK : null,
                            }}
                        >
                            <div
                                className="border-bottom"
                                style={{
                                    height: 200,
                                    overflow: "hidden",
                                    display: showData ? null : "none",
                                }}
                            >
                                <JSONEditor
                                    breaker={breaker}
                                    jsonObject={data}
                                    setBack={(object) => {
                                        setData(object);
                                    }}
                                />
                            </div>
                            <div
                                style={{
                                    padding: 20,
                                    overflowY: "scroll",
                                    height: `calc(100% - ${
                                        showData ? 200 : 0
                                    }px)`,
                                }}
                            >
                                <Callout
                                    icon={null}
                                    intent={error ? Intent.DANGER : null}
                                    style={{
                                        maxWidth: "100%",
                                        width: "fit-content",
                                    }}
                                >
                                    <div className="message-bubble-callout-content">
                                        {!error ? (
                                            <JsonForms
                                                schema={schema}
                                                uischema={uischema}
                                                data={data}
                                                cells={vanillaCells}
                                                renderers={JSONFORMS_RENDERERS}
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
                                                    style={{ marginTop: 10 }}
                                                    minimal
                                                    size={Size.LARGE}
                                                >
                                                    Click
                                                    <FAIcon
                                                        icon={faPlay}
                                                        style={{
                                                            color: Colors.GREEN2,
                                                            marginLeft: 10,
                                                            marginRight: 10,
                                                        }}
                                                    />
                                                    to re-run
                                                </Tag>
                                            </>
                                        )}
                                    </div>
                                </Callout>
                            </div>
                        </div>
                    </Allotment.Pane>
                </Allotment>
            </div>
        </div>
    );
}
export default withAutoSizer(withErrorBoundary(FormDesigner));

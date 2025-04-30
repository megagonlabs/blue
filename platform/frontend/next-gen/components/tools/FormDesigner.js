import { useGridStore } from "@/stores/grid-layout-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Checkbox,
    Divider,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    Popover,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowsFromDottedLine,
    faBinaryCircleCheck,
    faBinarySlash,
    faBookOpenCover,
    faBrowsers,
    faDownload,
    faPlay,
    faTrash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { Allotment } from "allotment";
import { clone } from "lodash";
import { createRef, useEffect, useRef, useState } from "react";
import { useErrorBoundary, withErrorBoundary } from "react-use-error-boundary";
import { v4 as uuidv4 } from "uuid";
import JsonEditor from "../codemirror/JSONEditor";
import { MIN_ALLOTMENT_PANE_SIZE } from "../constants";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import DocContainer from "../jsonforms/docs/DocContainer";
const DEFAULT_UI_SCHEMA = { type: "VerticalLayout", elements: [] };
const DEFAULT_SCHEMA = { type: "object", properties: {} };
const PANE_BUTTON_PROPS = {
    alignText: Alignment.START,
    fill: true,
    variant: ButtonVariant.MINIMAL,
};
function FormDesigner({ width, height }) {
    const addContainer = useGridStore((state) => state.addContainer);
    const idRef = useRef(null);
    const [error, resetError] = useErrorBoundary();
    const leftPaneRef = createRef();
    const [uischema, setUischema] = useState(clone(DEFAULT_UI_SCHEMA));
    const [schema, setSchema] = useState(clone(DEFAULT_SCHEMA));
    const [data, setData] = useState({});
    const [showData, setShowData] = useState(false);
    const [reset, setReset] = useState(false);
    useEffect(() => {
        if (!idRef.current) {
            idRef.current = uuidv4();
        }
    }, []);
    return (
        <div style={{ width, height }}>
            <div className="border-bottom" style={{ padding: 10 }}>
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    <Tooltip placement="bottom-start" content="Re-run">
                        <Button
                            intent={Intent.SUCCESS}
                            icon={<FAIcon icon={faPlay} />}
                        />
                    </Tooltip>
                    <Popover
                        minimal
                        placement="bottom"
                        content={
                            <Menu size={Size.LARGE}>
                                <MenuDivider title="Export" />
                                <MenuItem
                                    icon={<FAIcon icon={faBinaryCircleCheck} />}
                                    text="With data"
                                />
                                <MenuItem
                                    icon={<FAIcon icon={faBinarySlash} />}
                                    text="Without data"
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
                                content: "Form Docs.",
                                title: <DocContainer />,
                            })
                        }
                    />
                    <Divider />
                    <Button
                        intent={Intent.DANGER}
                        icon={<FAIcon icon={faTrash} />}
                        text="Reset all"
                        onClick={() => {
                            setReset(true);
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
                                    <JsonEditor
                                        reset={reset}
                                        jsonObject={uischema}
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
                                    <JsonEditor
                                        reset={reset}
                                        jsonObject={schema}
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
                                style={{ pointerEvents: "none" }}
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
                            style={{ maxHeight: "calc(100% - 51px)" }}
                        ></div>
                    </Allotment.Pane>
                </Allotment>
            </div>
        </div>
    );
}
export default withAutoSizer(withErrorBoundary(FormDesigner));

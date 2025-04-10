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
    faIndent,
    faPlay,
    faTrash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { Allotment } from "allotment";
import { createRef, useEffect, useRef, useState } from "react";
import { useErrorBoundary, withErrorBoundary } from "react-use-error-boundary";
import { v4 as uuidv4 } from "uuid";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import DocContainer from "../jsonforms/docs/DocContainer";
const MIN_ALLOTMENT_PANE_SIZE = 400;
const DEFAULT_UI_SCHEMA = JSON.stringify(
    { type: "VerticalLayout", elements: [] },
    null,
    4
);
const DEFAULT_SCHEMA = JSON.stringify(
    { type: "object", properties: {} },
    null,
    4
);
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
    const [jsonData, setJsonData] = useState("{}");
    const [jsonUischema, setJsonUischema] = useState(DEFAULT_UI_SCHEMA);
    const [jsonSchema, setJsonSchema] = useState(DEFAULT_SCHEMA);
    const [showData, setShowData] = useState(false);
    useEffect(() => {
        if (!idRef.current) idRef.current = uuidv4();
    }, []);
    return (
        <div style={{ width, height }}>
            <div className="border-bottom" style={{ padding: 10 }}>
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    <Tooltip placement="bottom-start" minimal content="Re-run">
                        <Button
                            intent={Intent.SUCCESS}
                            icon={<FAIcon icon={faPlay} />}
                        />
                    </Tooltip>
                    <Tooltip placement="bottom" minimal content="Format">
                        <Button icon={<FAIcon icon={faIndent} />} />
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
                        <Tooltip placement="bottom" minimal content="Export">
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
                            addContainer("Form Docs.", <DocContainer />)
                        }
                    />
                    <Divider />
                    <Button
                        intent={Intent.DANGER}
                        icon={<FAIcon icon={faTrash} />}
                        text="Reset all"
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
                                    <Tooltip
                                        fill
                                        minimal
                                        placement="bottom-start"
                                        content={
                                            "Describes how the form should be rendered"
                                        }
                                    >
                                        <Button
                                            {...PANE_BUTTON_PROPS}
                                            endIcon={
                                                <FAIcon
                                                    icon={
                                                        faArrowsFromDottedLine
                                                    }
                                                />
                                            }
                                            text="UI Schema"
                                        />
                                    </Tooltip>
                                </div>
                            </Allotment.Pane>
                            <Allotment.Pane minSize={200}>
                                <div
                                    className="border-bottom"
                                    style={{ padding: 10 }}
                                >
                                    <Tooltip
                                        fill
                                        minimal
                                        placement="bottom-start"
                                        content={
                                            "Describes the format of underlying data"
                                        }
                                    >
                                        <Button
                                            {...PANE_BUTTON_PROPS}
                                            endIcon={
                                                <FAIcon
                                                    icon={
                                                        faArrowsFromDottedLine
                                                    }
                                                />
                                            }
                                            text="Data Schema"
                                        />
                                    </Tooltip>
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

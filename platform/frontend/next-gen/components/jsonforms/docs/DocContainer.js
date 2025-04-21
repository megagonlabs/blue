import { useAppStore } from "@/stores/app-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Classes,
    Colors,
    Divider,
    Position,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import {
    faBookOpenCover,
    faInputNumeric,
    faInputText,
    faList,
    faListDropdown,
    faObjectGroup,
    faParagraph,
    faPause,
    faPlay,
    faPresentationScreen,
    faQuoteLeft,
    faRectanglesMixed,
    faSquareCheck,
    faSquareM,
    faTable,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useState } from "react";
import { FAIcon } from "../../FAIcon";
import withAutoSizer from "../../hocs/withAutoSizer";
import ArrayDoc from "./ArrayDoc";
import BasicsDoc from "./BasicsDoc";
import BooleanDoc from "./BooleanDoc";
import ButtonDoc from "./ButtonDoc";
import CalloutDoc from "./CalloutDoc";
import EnumDoc from "./EnumDoc";
import GroupDoc from "./GroupDoc";
import IntegerDoc from "./IntegerDoc";
import LabelDoc from "./LabelDoc";
import LayoutDoc from "./LayoutDoc";
import MarkdownDoc from "./MarkdownDoc";
import NumberDoc from "./NumberDoc";
import StringDoc from "./StringDoc";
import TableDoc from "./TableDoc";
import TabsDoc from "./TabsDoc";
import VegaDoc from "./VegaDoc";
const DOC_MENU = [
    {
        text: "Basics",
        icon: faBookOpenCover,
        label: "Documentation",
    },
    {
        text: "Array",
        icon: faList,
        label: "Inlined UI schema",
    },
    { text: "Boolean", icon: faSquareCheck },
    { text: "Button", icon: faPlay },
    { text: "Callout", icon: faQuoteLeft },
    { text: "Enum", icon: faListDropdown },
    { text: "Group", icon: faObjectGroup },
    { text: "Integer", icon: faInputNumeric },
    { text: "Label", icon: faParagraph },
    { text: "Layout", icon: faRectanglesMixed },
    { text: "Markdown", icon: faSquareM },
    { text: "Number", icon: faInputNumeric },
    { text: "String", icon: faInputText },
    { text: "Table", icon: faTable },
    { text: "Tabs", icon: faPause, iconClass: "fa-rotate-90" },
    {
        text: "Vega",
        icon: faPresentationScreen,
        label: "Vega-Lite",
    },
];
const DOCS = {
    basics: <BasicsDoc />,
    array: <ArrayDoc />,
    boolean: <BooleanDoc />,
    button: <ButtonDoc />,
    callout: <CalloutDoc />,
    enum: <EnumDoc />,
    group: <GroupDoc />,
    integer: <IntegerDoc />,
    label: <LabelDoc />,
    layout: <LayoutDoc />,
    markdown: <MarkdownDoc />,
    number: <NumberDoc />,
    string: <StringDoc />,
    table: <TableDoc />,
    tabs: <TabsDoc />,
    vega: <VegaDoc />,
};
function DocContainer({ width, height }) {
    const [focusTab, setFocusTab] = useState("basics");
    const darkMode = useAppStore((state) => state.darkMode);
    return (
        <div style={{ width, height }}>
            <div className="full-parent-dimension" style={{ display: "flex" }}>
                <div
                    style={{
                        padding: 10,
                        overflowY: "auto",
                        minWidth: 152.4,
                    }}
                    className="border-right"
                >
                    <ButtonGroup
                        vertical
                        size={Size.LARGE}
                        alignText={Alignment.START}
                        variant={ButtonVariant.MINIMAL}
                    >
                        {DOC_MENU.map((element) => (
                            <Tooltip
                                content={element.label}
                                placement={Position.RIGHT}
                            >
                                <Button
                                    active={_.isEqual(
                                        _.lowerCase(element.text),
                                        focusTab
                                    )}
                                    onClick={() =>
                                        setFocusTab(_.lowerCase(element.text))
                                    }
                                    text={element.text}
                                    icon={
                                        <FAIcon
                                            icon={element.icon}
                                            className={element.iconClass}
                                        />
                                    }
                                />
                            </Tooltip>
                        ))}
                        <Divider />
                        <Button text="Examples" />
                    </ButtonGroup>
                </div>
                <div
                    className={classNames(
                        "full-parent-dimension",
                        Classes.RUNNING_TEXT
                    )}
                    style={{
                        backgroundColor: darkMode ? Colors.BLACK : null,
                        padding: 20,
                        overflowY: "auto",
                    }}
                >
                    {_.get(DOCS, focusTab, null)}
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(DocContainer);

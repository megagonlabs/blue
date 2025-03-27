import { faIcon } from "@/components/icon";
import BooleanDoc from "@/components/jsonforms/docs/BooleanDoc";
import ButtonDoc from "@/components/jsonforms/docs/ButtonDoc";
import EnumDoc from "@/components/jsonforms/docs/EnumDoc";
import GroupDoc from "@/components/jsonforms/docs/GroupDoc";
import IntegerDoc from "@/components/jsonforms/docs/IntegerDoc";
import LabelDoc from "@/components/jsonforms/docs/LabelDoc";
import LayoutDoc from "@/components/jsonforms/docs/LayoutDoc";
import NumberDoc from "@/components/jsonforms/docs/NumberDoc";
import StringDoc from "@/components/jsonforms/docs/StringDoc";
import JsonViewer from "@/components/sessions/message/renderers/JsonViewer";
import {
    Button,
    Callout,
    Classes,
    Code,
    Drawer,
    HTMLTable,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    PanelStack2,
    Position,
    Tag,
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
    faPlay,
    faPresentationScreen,
    faRectangle,
    faRectanglesMixed,
    faSquareCheck,
    faSquareM,
    faTimes,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useCallback, useState } from "react";
import ArrayDoc from "./ArrayDoc";
import BasicsDoc from "./BasicsDoc";
import CalloutDoc from "./CalloutDoc";
import MarkdownDoc from "./MarkdownDoc";
import VegaDoc from "./VegaDoc";
const RendererDetailPanel = (props) => {
    const DOCS = {
        callout: <CalloutDoc closePanel={props.closePanel} />,
        boolean: <BooleanDoc closePanel={props.closePanel} />,
        button: <ButtonDoc closePanel={props.closePanel} />,
        enum: <EnumDoc closePanel={props.closePanel} />,
        group: <GroupDoc closePanel={props.closePanel} />,
        integer: <IntegerDoc closePanel={props.closePanel} />,
        label: <LabelDoc closePanel={props.closePanel} />,
        layout: <LayoutDoc closePanel={props.closePanel} />,
        number: <NumberDoc closePanel={props.closePanel} />,
        string: <StringDoc closePanel={props.closePanel} />,
        array: <ArrayDoc closePanel={props.closePanel} />,
        vega: <VegaDoc closePanel={props.closePanel} />,
        markdown: <MarkdownDoc closePanel={props.closePanel} />,
        basics: <BasicsDoc closePanel={props.closePanel} />,
    };
    return _.get(DOCS, props.type, null);
};
const MainMenuPanel = (props) => {
    const TYPES = [
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
        { text: "Callout", icon: faRectangle },
        { text: "Enum", icon: faListDropdown },
        { text: "Group", icon: faObjectGroup },
        { text: "Integer", icon: faInputNumeric },
        { text: "Label", icon: faParagraph },
        { text: "Layout", icon: faRectanglesMixed },
        { text: "Markdown", icon: faSquareM },
        { text: "Number", icon: faInputNumeric },
        { text: "String", icon: faInputText },
        {
            text: "Vega",
            icon: faPresentationScreen,
            label: "Vega-Lite",
        },
    ];
    const [openingPanel, setOpeningPanel] = useState(false);
    return (
        <div style={{ padding: 20 }}>
            <div style={{ position: "absolute", top: 13.25, right: 20 }}>
                <Tooltip
                    usePortal={false}
                    minimal
                    placement="bottom-end"
                    content="Close"
                >
                    <Button
                        large
                        minimal
                        icon={faIcon({ icon: faTimes })}
                        onClick={() => {
                            props.setIsDocOpen(false);
                            sessionStorage.setItem("isDocOpen", "false");
                        }}
                    />
                </Tooltip>
            </div>
            <Menu large style={{ padding: 0 }}>
                <MenuDivider title="UI Schema" />
                {TYPES.map((type, index) => (
                    <MenuItem
                        key={index}
                        icon={faIcon({
                            icon: type.icon,
                            size: 20,
                            style: { marginRight: 10, marginLeft: 4 },
                        })}
                        onClick={() => {
                            if (openingPanel) return;
                            setOpeningPanel(true);
                            props.openPanel({
                                props: { type: _.lowerCase(type.text) },
                                renderPanel: RendererDetailPanel,
                            });
                            setTimeout(() => {
                                setOpeningPanel(false);
                            }, 500);
                        }}
                        text={type.text}
                        label={
                            <span
                                className={Classes.TEXT_DISABLED}
                                style={{ marginRight: 4 }}
                            >
                                {type.label}
                            </span>
                        }
                    />
                ))}
                <MenuDivider title="Data Schema" />
                <HTMLTable style={{ width: "100%" }}>
                    <thead>
                        <tr>
                            <th>Props</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <Code>type</Code>
                            </td>
                            <td>
                                &quot;object&quot;, &quot;boolean&quot;,
                                &quot;integer&quot;, &quot;number&quot;,
                                &quot;string&quot;
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <Code>properties</Code>
                            </td>
                            <td>
                                <div>
                                    Define a mapping from string keys to values.
                                </div>
                                <Tag
                                    minimal
                                    intent={Intent.PRIMARY}
                                    style={{ marginTop: 5 }}
                                >
                                    Applies to type <strong>object</strong> only
                                </Tag>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <Code>enum</Code>
                            </td>
                            <td>
                                <div>
                                    Enables for a variable to be a set of
                                    pre-defined constants.
                                </div>
                                <Tag
                                    minimal
                                    intent={Intent.PRIMARY}
                                    style={{ marginTop: 5 }}
                                >
                                    Applies to type <strong>string</strong> only
                                </Tag>
                                <div className={Classes.RUNNING_TEXT}>
                                    <pre
                                        style={{
                                            position: "relative",
                                            overflow: "hidden",
                                        }}
                                    >
                                        <JsonViewer
                                            json={{
                                                example: {
                                                    type: "string",
                                                    enum: ["foo", "bar"],
                                                },
                                            }}
                                            enableClipboard={false}
                                        />
                                    </pre>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </HTMLTable>
                <MenuDivider title="Examples" />
                <Callout icon={null} intent={Intent.PRIMARY}>
                    Didn&apos;t find an useful example here? Please request for
                    an example by&nbsp;
                    <a
                        href="https://github.com/rit-git/blue/issues/new"
                        rel="noreferrer"
                        target="_blank"
                    >
                        creating an issue on Blue GitHub repository
                    </a>
                    .
                </Callout>
            </Menu>
        </div>
    );
};
export default function DocDrawer({ isOpen, setIsDocOpen }) {
    const initialPanel = {
        renderPanel: MainMenuPanel,
        props: { setIsDocOpen },
    };
    const [currentPanelStack, setCurrentPanelStack] = useState([initialPanel]);
    const addToPanelStack = useCallback((newPanel) => {
        setCurrentPanelStack((stack) => [...stack, newPanel]);
    }, []);
    const removeFromPanelStack = useCallback(() => {
        setCurrentPanelStack((stack) => stack.slice(0, -1));
    }, []);
    return (
        <Drawer
            isOpen={isOpen}
            hasBackdrop={false}
            enforceFocus={false}
            autoFocus
            canOutsideClickClose={false}
            canEscapeKeyClose
            position={Position.RIGHT}
            onClose={() => {
                setIsDocOpen(false);
                sessionStorage.setItem("isDocOpen", "false");
            }}
            style={{ zIndex: 36 }}
            size={"min(40%, 716.8px)"}
        >
            <PanelStack2
                renderActivePanelOnly={false}
                className="full-parent-height transition-none"
                onOpen={addToPanelStack}
                onClose={removeFromPanelStack}
                showPanelHeader={false}
                stack={currentPanelStack}
            />
        </Drawer>
    );
}

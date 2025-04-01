import { AuthContext } from "@/components/contexts/auth-context";
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
    Colors,
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
    faPause,
    faPlay,
    faPresentationScreen,
    faRectangle,
    faRectanglesMixed,
    faSquareCheck,
    faSquareM,
    faTable,
    faTimes,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useCallback, useContext, useState } from "react";
import CandidatesTable from "../examples/CandidatesTable";
import ArrayDoc from "./ArrayDoc";
import BasicsDoc from "./BasicsDoc";
import CalloutDoc from "./CalloutDoc";
import MarkdownDoc from "./MarkdownDoc";
import TableDoc from "./TableDoc";
import TabsDoc from "./TabsDoc";
import VegaDoc from "./VegaDoc";
const EXAMPLE_LIST = [
    {
        id: "candidates-table",
        title: "Candidates table",
        icon: faTable,
        description:
            "Table view for a list of candidates with name, job title, and skill matches.",
    },
];
const RendererExamplePanel = ({
    closePanel,
    id,
    setJsonUischema,
    setData,
    setJsonSchema,
}) => {
    const EXAMPLES = {
        "candidates-table": (
            <CandidatesTable
                setJsonUischema={setJsonUischema}
                setData={setData}
                setJsonSchema={setJsonSchema}
                closePanel={closePanel}
            />
        ),
    };
    return _.get(EXAMPLES, id, null);
};
const RendererDetailPanel = ({ closePanel, type }) => {
    const DOCS = {
        callout: <CalloutDoc closePanel={closePanel} />,
        boolean: <BooleanDoc closePanel={closePanel} />,
        button: <ButtonDoc closePanel={closePanel} />,
        enum: <EnumDoc closePanel={closePanel} />,
        group: <GroupDoc closePanel={closePanel} />,
        integer: <IntegerDoc closePanel={closePanel} />,
        label: <LabelDoc closePanel={closePanel} />,
        layout: <LayoutDoc closePanel={closePanel} />,
        number: <NumberDoc closePanel={closePanel} />,
        string: <StringDoc closePanel={closePanel} />,
        array: <ArrayDoc closePanel={closePanel} />,
        vega: <VegaDoc closePanel={closePanel} />,
        markdown: <MarkdownDoc closePanel={closePanel} />,
        basics: <BasicsDoc closePanel={closePanel} />,
        tabs: <TabsDoc closePanel={closePanel} />,
        table: <TableDoc closePanel={closePanel} />,
    };
    return _.get(DOCS, type, null);
};
const MainMenuPanel = ({
    openPanel,
    setIsDocOpen,
    setJsonUischema,
    setData,
    setJsonSchema,
}) => {
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
        { text: "Table", icon: faTable },
        { text: "Tabs", icon: faPause, iconClass: "fa-rotate-90" },
        {
            text: "Vega",
            icon: faPresentationScreen,
            label: "Vega-Lite",
        },
    ];
    const [openingPanel, setOpeningPanel] = useState(false);
    const { settings } = useContext(AuthContext);
    const darkMode = _.get(settings, "dark_mode", false);
    return (
        <div
            style={{
                padding: 20,
                backgroundColor: darkMode ? Colors.DARK_GRAY2 : Colors.WHITE,
            }}
        >
            <div style={{ position: "absolute", top: 13.25, right: 20 }}>
                <Tooltip
                    usePortal={false}
                    minimal
                    placement="bottom-end"
                    content="Close"
                >
                    <Button
                        size="large"
                        variant="minimal"
                        icon={faIcon({ icon: faTimes })}
                        onClick={() => {
                            setIsDocOpen(false);
                            sessionStorage.setItem("isDocOpen", "false");
                        }}
                    />
                </Tooltip>
            </div>
            <Menu
                size="large"
                style={{
                    padding: 0,
                    backgroundColor: darkMode ? Colors.DARK_GRAY2 : null,
                }}
            >
                <MenuDivider title="UI Schema" />
                {TYPES.map((type, index) => (
                    <MenuItem
                        key={index}
                        icon={faIcon({
                            icon: type.icon,
                            size: 20,
                            className: type.iconClass,
                            style: { marginRight: 10, marginLeft: 4 },
                        })}
                        onClick={() => {
                            if (openingPanel) return;
                            setOpeningPanel(true);
                            openPanel({
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
                <div style={{ marginBottom: 15 }}>
                    <Menu size="large" style={{ padding: 0 }}>
                        {EXAMPLE_LIST.map((example, index) => (
                            <MenuItem
                                key={index}
                                icon={faIcon({
                                    icon: example.icon,
                                    style: { marginLeft: 4 },
                                })}
                                onClick={() => {
                                    if (openingPanel) return;
                                    setOpeningPanel(true);
                                    openPanel({
                                        props: {
                                            id: example.id,
                                            setJsonUischema,
                                            setData,
                                            setJsonSchema,
                                        },
                                        renderPanel: RendererExamplePanel,
                                    });
                                    setTimeout(() => {
                                        setOpeningPanel(false);
                                    }, 500);
                                }}
                                text={
                                    <div style={{ marginLeft: 3 }}>
                                        <div>{example.title}</div>
                                        <div
                                            style={{
                                                marginTop: 5,
                                                whiteSpace: "initial",
                                                lineHeight: "initial",
                                            }}
                                            className={classNames(
                                                Classes.TEXT_SMALL,
                                                Classes.TEXT_MUTED
                                            )}
                                        >
                                            {example.description}
                                        </div>
                                    </div>
                                }
                            />
                        ))}
                    </Menu>
                </div>
                <Callout icon={null} intent={Intent.PRIMARY}>
                    Didn&apos;t find an useful example here? Please request for
                    an example by&nbsp;
                    <a
                        href="https://github.com/megagonlabs/blue/issues/new"
                        rel="noopener noreferrer"
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
export default function DocDrawer({
    isOpen,
    setIsDocOpen,
    setJsonUischema,
    setData,
    setJsonSchema,
}) {
    const initialPanel = {
        renderPanel: MainMenuPanel,
        props: { setIsDocOpen, setJsonUischema, setData, setJsonSchema },
    };
    const [currentPanelStack, setCurrentPanelStack] = useState([initialPanel]);
    const addToPanelStack = useCallback((newPanel) => {
        setCurrentPanelStack((stack) => [...stack, newPanel]);
    }, []);
    const removeFromPanelStack = useCallback(() => {
        setCurrentPanelStack((stack) => stack.slice(0, -1));
    }, []);
    const { settings } = useContext(AuthContext);
    const darkMode = _.get(settings, "dark_mode", false);
    return (
        <Drawer
            className={darkMode ? Classes.DARK : null}
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
            style={{ zIndex: 36, padding: 1 }}
            size={"min(40%, 716.8px)"}
        >
            <PanelStack2
                renderActivePanelOnly
                className="full-parent-height transition-none"
                onOpen={addToPanelStack}
                onClose={removeFromPanelStack}
                showPanelHeader={false}
                stack={currentPanelStack}
            />
        </Drawer>
    );
}

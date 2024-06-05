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
import {
    Button,
    Callout,
    Code,
    Drawer,
    HTMLTable,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    PanelStack2,
    Position,
    Pre,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faInputNumeric,
    faInputText,
    faListDropdown,
    faObjectGroup,
    faParagraph,
    faPlay,
    faRectanglesMixed,
    faSquareCheck,
    faTimes,
} from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useCallback, useState } from "react";
const RendererDetailPanel = (props) => {
    const DOCS = {
        boolean: <BooleanDoc closePanel={props.closePanel} />,
        button: <ButtonDoc closePanel={props.closePanel} />,
        enum: <EnumDoc closePanel={props.closePanel} />,
        group: <GroupDoc closePanel={props.closePanel} />,
        integer: <IntegerDoc closePanel={props.closePanel} />,
        label: <LabelDoc closePanel={props.closePanel} />,
        layout: <LayoutDoc closePanel={props.closePanel} />,
        number: <NumberDoc closePanel={props.closePanel} />,
        string: <StringDoc closePanel={props.closePanel} />,
    };
    return _.get(DOCS, props.type, null);
};
const MainMenuPanel = (props) => {
    const TYPES = [
        { text: "Boolean", icon: faSquareCheck },
        { text: "Button", icon: faPlay },
        { text: "Enum", icon: faListDropdown },
        { text: "Group", icon: faObjectGroup },
        { text: "Integer", icon: faInputNumeric },
        { text: "Label", icon: faParagraph },
        { text: "Layout", icon: faRectanglesMixed },
        { text: "Number", icon: faInputNumeric },
        { text: "String", icon: faInputText },
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
                        onClick={() => props.setIsDocOpen(false)}
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
                                    Applies to type &quot;
                                    <strong>object</strong>&quot; only
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
                                    Applies to type &quot;
                                    <strong>string</strong>&quot; only
                                </Tag>
                                <Pre>
                                    {JSON.stringify(
                                        {
                                            example: {
                                                type: "string",
                                                enum: ["foo", "bar", "foobar"],
                                            },
                                        },
                                        null,
                                        4
                                    )}
                                </Pre>
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
            }}
            style={{ zIndex: 36 }}
            size={"min(40%, 716.8px)"}
        >
            <PanelStack2
                className="full-parent-height"
                onOpen={addToPanelStack}
                onClose={removeFromPanelStack}
                showPanelHeader={false}
                stack={currentPanelStack}
            />
        </Drawer>
    );
}

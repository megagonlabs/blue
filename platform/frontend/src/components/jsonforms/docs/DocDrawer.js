import { faIcon } from "@/components/icon";
import {
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
} from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useCallback, useState } from "react";
import BooleanDoc from "./BooleanDoc";
import ButtonDoc from "./ButtonDoc";
import EnumDoc from "./EnumDoc";
import GroupDoc from "./GroupDoc";
import IntegerDoc from "./IntegerDoc";
import LabelDoc from "./LabelDoc";
import LayoutDoc from "./LayoutDoc";
import NumberDoc from "./NumberDoc";
import StringDoc from "./StringDoc";
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
    return (
        <div style={{ padding: 20 }}>
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
                            props.openPanel({
                                props: { type: _.lowerCase(type.text) },
                                renderPanel: RendererDetailPanel,
                            });
                        }}
                        text={type.text}
                    />
                ))}
                <MenuDivider title="Schema" />
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
                                    predefined constants.
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
            </Menu>
        </div>
    );
};
export default function DocDrawer({ isOpen, setIsDocOpen }) {
    const initialPanel = { renderPanel: MainMenuPanel };
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

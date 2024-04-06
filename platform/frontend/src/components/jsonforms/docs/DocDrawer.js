import { faIcon } from "@/components/icon";
import {
    Drawer,
    Menu,
    MenuDivider,
    MenuItem,
    PanelStack2,
    Position,
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
                            style: { marginRight: 10 },
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

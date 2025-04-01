import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Card,
    Classes,
    Colors,
    HotkeysProvider,
    HotkeysTarget2,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    Size,
} from "@blueprintjs/core";
import { Omnibar } from "@blueprintjs/select";
import {
    faCircleA,
    faCube,
    faFunction,
    faInboxFull,
    faInboxOut,
    faLayerGroup,
    faMagnifyingGlass,
    faPencilRuler,
    faScrewdriverWrench,
    faServer,
    faUserGroup,
    faWavePulse,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import Image from "next/image";
import ExpandingBox from "./ExpandingBox";
import { FAIcon } from "./FAIcon";
import FormDesigner from "./tools/FormDesigner";

export default function Blue({ children }) {
    const addContainer = useGridStore((state) => state.addContainer);
    const openOmnibar = useAppStore((state) => state.openOmnibar);
    const setState = useAppStore((state) => state.setState);
    const showOmnibar = useAppStore((state) => state.showOmnibar);
    const darkMode = useAppStore((state) => state.darkMode);
    const closeOmnibar = useAppStore((state) => state.closeOmnibar);
    const omnibarItems = useAppStore((state) => state.omnibarItems);
    const hotkeys = [
        {
            combo: "shift + s",
            global: true,
            label: "Show omnibar",
            onKeyDown: openOmnibar,
            // prevent typing "O" in omnibar input
            preventDefault: true,
        },
        {
            combo: "shift + d",
            global: true,
            label: "Toggle theme",
            onKeyDown: () => setState({ key: "darkMode", value: !darkMode }),
        },
    ];
    const darkModeClassName = darkMode ? Classes.DARK : null;
    return (
        <HotkeysProvider dialogProps={{ className: darkModeClassName }}>
            <HotkeysTarget2 hotkeys={hotkeys}>
                <div
                    className={darkModeClassName}
                    style={{
                        height: "100vh",
                        width: "100vw",
                        backgroundColor: darkMode
                            ? Colors.DARK_GRAY1
                            : Colors.LIGHT_GRAY5,
                    }}
                >
                    <Omnibar
                        className={darkModeClassName}
                        inputProps={{
                            size: Size.LARGE,
                            placeholder: null,
                            leftIcon: <FAIcon icon={faMagnifyingGlass} />,
                        }}
                        onClose={closeOmnibar}
                        isOpen={showOmnibar}
                        items={omnibarItems}
                    />
                    <div
                        style={{
                            position: "absolute",
                            top: 20,
                            left: 20,
                            zIndex: 4,
                        }}
                    >
                        <ExpandingBox
                            initialWidth={65}
                            initialHeight={65}
                            expandedWidth={250}
                            expandedHeight={740}
                        >
                            {(isExpanded) => (
                                <Card
                                    interactive
                                    style={{
                                        width: "100%",
                                        height: "100%",
                                        overflow: isExpanded
                                            ? "auto"
                                            : "hidden",
                                    }}
                                >
                                    <Image
                                        width={25}
                                        height={25}
                                        src="/images/logo.png"
                                        alt="Megagon Labs logo"
                                    />
                                    {isExpanded && (
                                        <div style={{ marginTop: 20 }}>
                                            <Menu
                                                style={{
                                                    padding: 0,
                                                    backgroundColor: darkMode
                                                        ? Colors.DARK_GRAY2
                                                        : null,
                                                }}
                                                size={Size.LARGE}
                                            >
                                                <MenuDivider title="Sessions" />
                                                <MenuItem
                                                    text="All Sessions"
                                                    icon={
                                                        <FAIcon
                                                            style={{
                                                                marginRight: 5,
                                                            }}
                                                            icon={faInboxFull}
                                                        />
                                                    }
                                                />
                                                <MenuItem
                                                    intent={Intent.PRIMARY}
                                                    text="New Session"
                                                    icon={
                                                        <FAIcon
                                                            style={{
                                                                marginRight: 5,
                                                            }}
                                                            icon={faInboxOut}
                                                        />
                                                    }
                                                />
                                                <MenuDivider title="Registries" />
                                                <MenuItem
                                                    text="Agent"
                                                    icon={
                                                        <FAIcon
                                                            style={{
                                                                marginRight: 5,
                                                            }}
                                                            icon={faCircleA}
                                                        />
                                                    }
                                                />
                                                <MenuItem
                                                    text="Data"
                                                    icon={
                                                        <FAIcon
                                                            style={{
                                                                marginRight: 5,
                                                            }}
                                                            icon={faServer}
                                                        />
                                                    }
                                                />
                                                <MenuItem
                                                    text="Operator"
                                                    icon={
                                                        <FAIcon
                                                            style={{
                                                                marginRight: 5,
                                                            }}
                                                            icon={faFunction}
                                                        />
                                                    }
                                                />
                                                <MenuItem
                                                    text="Model"
                                                    icon={
                                                        <FAIcon
                                                            style={{
                                                                marginRight: 5,
                                                            }}
                                                            icon={faCube}
                                                        />
                                                    }
                                                />
                                                <MenuDivider title="Tools" />
                                                <MenuItem
                                                    onClick={() =>
                                                        addContainer(
                                                            "Form Designer",
                                                            <FormDesigner />
                                                        )
                                                    }
                                                    text="Form Designer"
                                                    icon={
                                                        <FAIcon
                                                            style={{
                                                                marginRight: 5,
                                                            }}
                                                            icon={faPencilRuler}
                                                        />
                                                    }
                                                />
                                                <MenuDivider title="Administrator" />
                                                <MenuItem
                                                    text="System Status"
                                                    icon={
                                                        <FAIcon
                                                            style={{
                                                                marginRight: 5,
                                                            }}
                                                            icon={faWavePulse}
                                                        />
                                                    }
                                                />
                                                <MenuItem
                                                    text="Agents"
                                                    icon={
                                                        <FAIcon
                                                            style={{
                                                                marginRight: 5,
                                                            }}
                                                            icon={faCircleA}
                                                        />
                                                    }
                                                />
                                                <MenuItem
                                                    text="Services"
                                                    icon={
                                                        <FAIcon
                                                            style={{
                                                                marginRight: 5,
                                                            }}
                                                            icon={faLayerGroup}
                                                        />
                                                    }
                                                />
                                                <MenuItem
                                                    text="Users"
                                                    icon={
                                                        <FAIcon
                                                            style={{
                                                                marginRight: 5,
                                                            }}
                                                            icon={faUserGroup}
                                                        />
                                                    }
                                                />
                                                <MenuItem
                                                    text="Configurations"
                                                    icon={
                                                        <FAIcon
                                                            style={{
                                                                marginRight: 5,
                                                            }}
                                                            icon={
                                                                faScrewdriverWrench
                                                            }
                                                        />
                                                    }
                                                />
                                            </Menu>
                                        </div>
                                    )}
                                </Card>
                            )}
                        </ExpandingBox>
                    </div>
                    <div
                        className="full-parent-dimension"
                        style={{ padding: "20px 20px 20px 105px" }}
                    >
                        <div
                            className="border-radius-2 full-parent-dimension overflow-hidden"
                            style={{
                                backgroundColor: darkMode
                                    ? Colors.DARK_GRAY3
                                    : Colors.LIGHT_GRAY3,
                            }}
                        >
                            {children}
                        </div>
                    </div>
                </div>
            </HotkeysTarget2>
        </HotkeysProvider>
    );
}

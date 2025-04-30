import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useSessionStore } from "@/stores/session-store";
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
    OverlaysProvider,
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
import _ from "lodash";
import Image from "next/image";
import { useShallow } from "zustand/react/shallow";
import AccountPanel from "./AccountPanel";
import SystemStatusContainer from "./administrator/SystemStatusContainer";
import AgentList from "./agents/AgentList";
import Authentication from "./Authentication";
import ExpandingBox from "./ExpandingBox";
import { FAIcon } from "./FAIcon";
import SessionList from "./sessions/SessionList";
import FormDesigner from "./tools/FormDesigner";
export default function Blue({ children }) {
    const {
        showOmnibar,
        darkMode,
        omnibarItems,
        openOmnibar,
        setState,
        closeOmnibar,
    } = useAppStore(
        useShallow((state) => ({
            showOmnibar: state.showOmnibar,
            darkMode: state.darkMode,
            omnibarItems: state.omnibarItems,
            openOmnibar: state.openOmnibar,
            setState: state.setState,
            closeOmnibar: state.closeOmnibar,
        }))
    );
    const addContainer = useGridStore((state) => state.addContainer);
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
    const user = useAuthStore((state) => state.user);
    const createNewSession = useSessionStore((state) => state.createNewSession);
    if (_.isNull(user)) {
        return <Authentication />;
    }
    return (
        <OverlaysProvider>
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
                                bottom: 20,
                                left: 20,
                                zIndex: 19,
                            }}
                        >
                            <ExpandingBox
                                initialWidth={65}
                                initialHeight={65}
                                expandedWidth={340}
                                expandedHeight={141.43}
                            >
                                {(isExpanded) => (
                                    <AccountPanel isExpanded={isExpanded} />
                                )}
                            </ExpandingBox>
                        </div>
                        <div
                            style={{
                                position: "absolute",
                                top: 20,
                                left: 20,
                                zIndex: 19,
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
                                        className="full-parent-dimension border-radius-10"
                                        style={{
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
                                                        backgroundColor:
                                                            darkMode
                                                                ? Colors.DARK_GRAY2
                                                                : null,
                                                    }}
                                                    size={Size.LARGE}
                                                >
                                                    <MenuDivider title="Sessions" />
                                                    <MenuItem
                                                        onClick={() =>
                                                            addContainer({
                                                                title: "Sessions",
                                                                content: (
                                                                    <SessionList />
                                                                ),
                                                            })
                                                        }
                                                        text="All Sessions"
                                                        icon={
                                                            <FAIcon
                                                                style={{
                                                                    marginRight: 3,
                                                                }}
                                                                icon={
                                                                    faInboxFull
                                                                }
                                                            />
                                                        }
                                                    />
                                                    <MenuItem
                                                        intent={Intent.PRIMARY}
                                                        text="New Session"
                                                        onClick={() =>
                                                            createNewSession()
                                                        }
                                                        icon={
                                                            <FAIcon
                                                                style={{
                                                                    marginRight: 3,
                                                                }}
                                                                icon={
                                                                    faInboxOut
                                                                }
                                                            />
                                                        }
                                                    />
                                                    <MenuDivider title="Registries" />
                                                    <MenuItem
                                                        onClick={() =>
                                                            addContainer({
                                                                title: "Agent Registry",
                                                                content: (
                                                                    <AgentList />
                                                                ),
                                                            })
                                                        }
                                                        text="Agent"
                                                        icon={
                                                            <FAIcon
                                                                style={{
                                                                    marginRight: 3,
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
                                                                    marginRight: 3,
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
                                                                    marginRight: 3,
                                                                }}
                                                                icon={
                                                                    faFunction
                                                                }
                                                            />
                                                        }
                                                    />
                                                    <MenuItem
                                                        text="Model"
                                                        icon={
                                                            <FAIcon
                                                                style={{
                                                                    marginRight: 3,
                                                                }}
                                                                icon={faCube}
                                                            />
                                                        }
                                                    />
                                                    <MenuDivider title="Tools" />
                                                    <MenuItem
                                                        onClick={() =>
                                                            addContainer({
                                                                title: "Form Designer",
                                                                content: (
                                                                    <FormDesigner />
                                                                ),
                                                            })
                                                        }
                                                        text="Form Designer"
                                                        icon={
                                                            <FAIcon
                                                                style={{
                                                                    marginRight: 3,
                                                                }}
                                                                icon={
                                                                    faPencilRuler
                                                                }
                                                            />
                                                        }
                                                    />
                                                    <MenuDivider title="Administrator" />
                                                    <MenuItem
                                                        onClick={() =>
                                                            addContainer({
                                                                title: "Sessions",
                                                                content: (
                                                                    <SystemStatusContainer />
                                                                ),
                                                            })
                                                        }
                                                        text="System Status"
                                                        icon={
                                                            <FAIcon
                                                                style={{
                                                                    marginRight: 3,
                                                                }}
                                                                icon={
                                                                    faWavePulse
                                                                }
                                                            />
                                                        }
                                                    />
                                                    <MenuItem
                                                        text="Agents"
                                                        icon={
                                                            <FAIcon
                                                                style={{
                                                                    marginRight: 3,
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
                                                                    marginRight: 3,
                                                                }}
                                                                icon={
                                                                    faLayerGroup
                                                                }
                                                            />
                                                        }
                                                    />
                                                    <MenuItem
                                                        text="Users"
                                                        icon={
                                                            <FAIcon
                                                                style={{
                                                                    marginRight: 3,
                                                                }}
                                                                icon={
                                                                    faUserGroup
                                                                }
                                                            />
                                                        }
                                                    />
                                                    <MenuItem
                                                        text="Configurations"
                                                        icon={
                                                            <FAIcon
                                                                style={{
                                                                    marginRight: 3,
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
                                className="border-radius-10 full-parent-dimension overflow-hidden"
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
        </OverlaysProvider>
    );
}

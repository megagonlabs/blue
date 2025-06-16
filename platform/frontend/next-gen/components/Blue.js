import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useSessionStore } from "@/stores/session-store";
import { useSystemStatusStore } from "@/stores/system-status-store";
import {
    Alert,
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
    faCircleDot,
    faInboxFull,
    faInboxOut,
    faLayerGroup,
    faMagnifyingGlass,
    faPencilRuler,
    faScrewdriverWrench,
    faUserGroup,
    faWavePulse,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import Image from "next/image";
import { useShallow } from "zustand/react/shallow";
import AccountPanel from "./AccountPanel";
import Authentication from "./Authentication";
import { ENTITY_TYPE_LOOKUP } from "./constants";
import ExpandingBox from "./ExpandingBox";
import { FAIcon } from "./FAIcon";
import PlatformAgents from "./platforms/PlatformAgents";
import PlatformConfigurations from "./platforms/PlatformConfigurations";
import PlatformServices from "./platforms/PlatformServices";
import PlatformUsers from "./platforms/PlatformUsers";
import SystemStatusContainer from "./platforms/SystemStatusContainer";
import AgentList from "./registries/agents/AgentList";
import SourceList from "./registries/data/SourceList";
import ModelList from "./registries/models/ModelList";
import OperatorList from "./registries/operators/OperatorList";
import ToolList from "./registries/tools/ToolList";
import DemoContainer from "./sessions/DemoContainer";
import SessionList from "./sessions/SessionList";
import FormDesigner from "./tools/FormDesigner";
const AGENT_GROUP_ICON = _.get(ENTITY_TYPE_LOOKUP, "agent_group.icon", null);
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
            darkMode: state.dark_mode,
            omnibarItems: state.omnibarItems,
            openOmnibar: state.openOmnibar,
            setState: state.setState,
            closeOmnibar: state.closeOmnibar,
        }))
    );
    const isSystemStatusLive = useSystemStatusStore((state) => state.live);
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
            onKeyDown: () => {
                axios.put(`/accounts/profile/settings/dark_mode`, {
                    value: !darkMode,
                });
                setState({ key: "dark_mode", value: !darkMode });
            },
        },
    ];
    const darkModeClassName = darkMode ? Classes.DARK : null;
    const { user, permissions, logout } = useAuthStore(
        useShallow((state) => ({
            user: state.user,
            permissions: state.permissions,
            logout: state.logout,
        }))
    );
    const REGISTRY_MENU_ITEMS = {
        agent: {
            title: "Agent Registry",
            text: "Agent",
            content: <AgentList />,
            visible: permissions.canReadAgentRegistry,
        },
        source: {
            title: "Data Registry",
            text: "Data",
            content: <SourceList />,
            visible: permissions.canReadDataRegistry,
        },
        operator: {
            title: "Operator Registry",
            text: "Operator",
            content: <OperatorList />,
            visible: permissions.canReadOperatorRegistry,
        },
        model: {
            title: "Model Registry",
            text: "Model",
            content: <ModelList />,
            visible: permissions.canReadModelRegistry,
        },
        server: {
            title: "Tool Registry",
            text: "Tool",
            content: <ToolList />,
            visible: permissions.canReadToolRegistry,
        },
    };
    const createNewSession = useSessionStore((state) => state.createNewSession);
    const userProfileError =
        !_.isEmpty(user) && _.isEmpty(_.get(user, "role", null));
    const PLATFORM_SECTION_MENU_ITEMS = {
        systemStatus: {
            title: "System Status",
            text: "System Status",
            icon: faWavePulse,
            content: <SystemStatusContainer />,
            visible: permissions.canReadPlatformStatus,
            labelElement: isSystemStatusLive && (
                <FAIcon
                    icon={faCircleDot}
                    className="fa-fade"
                    style={{
                        "--fa-animation-duration": "2s",
                        color: Colors.GREEN3,
                    }}
                />
            ),
        },
        agents: {
            title: "Platform Agents",
            text: "Agents",
            icon: faCircleA,
            content: <PlatformAgents />,
            visible: permissions.canReadPlatformAgents,
        },
        services: {
            title: "Platform Services",
            text: "Services",
            icon: faLayerGroup,
            content: <PlatformServices />,
            visible: permissions.canReadPlatformServices,
        },
        users: {
            title: "Platform Users",
            text: "Users",
            icon: faUserGroup,
            content: <PlatformUsers />,
            visible: permissions.canWritePlatformUsers,
        },
        configurations: {
            title: "Platform Configurations",
            text: "Configurations",
            content: <PlatformConfigurations />,
            icon: faScrewdriverWrench,
            visible: permissions.canWritePlatformSettings,
        },
    };
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
                                            padding: darkMode ? 1 : 0,
                                            position: "relative",
                                            overflow: "hidden",
                                        }}
                                    >
                                        <div
                                            className="full-parent-dimension border-radius-10"
                                            style={{
                                                padding: 20,
                                                overflow: isExpanded
                                                    ? "auto"
                                                    : "hidden",
                                            }}
                                        >
                                            <div
                                                style={{
                                                    position: "sticky",
                                                    top: 0,
                                                    left: 0,
                                                    zIndex: 1,
                                                }}
                                            >
                                                <Image
                                                    style={{
                                                        position: "sticky",
                                                        top: 0,
                                                        left: 0,
                                                        zIndex: 1,
                                                    }}
                                                    width={25}
                                                    height={25}
                                                    src="/images/logo.png"
                                                    alt="Megagon Labs logo"
                                                />
                                                <div
                                                    className="full-parent-width"
                                                    style={{
                                                        background: darkMode
                                                            ? "linear-gradient(to bottom, rgba(37,42,49,1) 0%, rgba(37,42,49,1) 65px, rgba(255,255,255,0) 99%, rgba(255,255,255,0) 100%)"
                                                            : "linear-gradient(to bottom, rgba(255,255,255,1) 0%, rgba(255,255,255,1) 65px, rgba(255,255,255,0) 99%, rgba(255,255,255,0) 100%)",
                                                        height: 85,
                                                        position: "absolute",
                                                        borderTopLeftRadius: 10,
                                                        borderTopRightRadius: 10,
                                                        width: "calc(100% + 40px)",
                                                        top: -20,
                                                        left: -20,
                                                    }}
                                                />
                                            </div>
                                            {isExpanded && (
                                                <div style={{ marginTop: 30 }}>
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
                                                        {_.some([
                                                            permissions.canReadSessions,
                                                            permissions.canWriteSessions,
                                                        ]) && (
                                                            <>
                                                                <MenuDivider title="Sessions" />
                                                                <MenuItem
                                                                    onClick={() =>
                                                                        addContainer(
                                                                            {
                                                                                title: "Sessions",
                                                                                content:
                                                                                    (
                                                                                        <SessionList />
                                                                                    ),
                                                                            }
                                                                        )
                                                                    }
                                                                    text="All Sessions"
                                                                    icon={
                                                                        <FAIcon
                                                                            icon={
                                                                                faInboxFull
                                                                            }
                                                                        />
                                                                    }
                                                                />
                                                                {permissions.canWriteSessions && (
                                                                    <MenuItem
                                                                        intent={
                                                                            Intent.PRIMARY
                                                                        }
                                                                        text="New Session"
                                                                        onClick={() =>
                                                                            createNewSession()
                                                                        }
                                                                        icon={
                                                                            <FAIcon
                                                                                icon={
                                                                                    faInboxOut
                                                                                }
                                                                            />
                                                                        }
                                                                    />
                                                                )}
                                                            </>
                                                        )}
                                                        {_.some([
                                                            permissions.canReadAgentRegistry,
                                                            permissions.canReadDataRegistry,
                                                            permissions.canReadOperatorRegistry,
                                                            permissions.canReadModelRegistry,
                                                            permissions.canReadToolRegistry,
                                                        ]) && (
                                                            <>
                                                                {permissions.canReadAgentRegistry && (
                                                                    <MenuItem
                                                                        intent={
                                                                            Intent.SUCCESS
                                                                        }
                                                                        icon={
                                                                            <FAIcon
                                                                                icon={
                                                                                    AGENT_GROUP_ICON
                                                                                }
                                                                            />
                                                                        }
                                                                        text="Demos"
                                                                        onClick={() => {
                                                                            addContainer(
                                                                                {
                                                                                    icon: AGENT_GROUP_ICON,
                                                                                    title: "Demos",
                                                                                    content:
                                                                                        (
                                                                                            <DemoContainer />
                                                                                        ),
                                                                                    uid: `DemoContainer`,
                                                                                }
                                                                            );
                                                                        }}
                                                                    />
                                                                )}
                                                                <MenuDivider title="Registries" />
                                                                {[
                                                                    "agent",
                                                                    "source",
                                                                    "operator",
                                                                    "model",
                                                                    "server",
                                                                ].map(
                                                                    (type) => {
                                                                        const {
                                                                            title,
                                                                            text,
                                                                            content,
                                                                            visible,
                                                                        } =
                                                                            REGISTRY_MENU_ITEMS[
                                                                                type
                                                                            ];
                                                                        const {
                                                                            icon,
                                                                        } =
                                                                            ENTITY_TYPE_LOOKUP[
                                                                                type
                                                                            ];
                                                                        return (
                                                                            visible && (
                                                                                <MenuItem
                                                                                    onClick={() => {
                                                                                        addContainer(
                                                                                            {
                                                                                                icon,
                                                                                                title,
                                                                                                content,
                                                                                            }
                                                                                        );
                                                                                    }}
                                                                                    text={
                                                                                        text
                                                                                    }
                                                                                    icon={
                                                                                        <FAIcon
                                                                                            icon={
                                                                                                icon
                                                                                            }
                                                                                        />
                                                                                    }
                                                                                />
                                                                            )
                                                                        );
                                                                    }
                                                                )}
                                                            </>
                                                        )}
                                                        {_.some([
                                                            permissions.showFormDesigner,
                                                        ]) && (
                                                            <>
                                                                <MenuDivider title="Tools" />
                                                                {permissions.showFormDesigner && (
                                                                    <MenuItem
                                                                        onClick={() =>
                                                                            addContainer(
                                                                                {
                                                                                    title: "Form Designer",
                                                                                    content:
                                                                                        (
                                                                                            <FormDesigner />
                                                                                        ),
                                                                                }
                                                                            )
                                                                        }
                                                                        text="Form Designer"
                                                                        icon={
                                                                            <FAIcon
                                                                                icon={
                                                                                    faPencilRuler
                                                                                }
                                                                            />
                                                                        }
                                                                    />
                                                                )}
                                                            </>
                                                        )}
                                                        {_.some([
                                                            permissions.canReadPlatformStatus,
                                                            permissions.canReadPlatformAgents,
                                                            permissions.canReadPlatformServices,
                                                            permissions.canWritePlatformUsers,
                                                            permissions.canWritePlatformSettings,
                                                        ]) && (
                                                            <>
                                                                <MenuDivider title="Platform" />
                                                                {[
                                                                    "systemStatus",
                                                                    "agents",
                                                                    "services",
                                                                    "users",
                                                                    "configurations",
                                                                ].map((key) => {
                                                                    const {
                                                                        text,
                                                                        title,
                                                                        content,
                                                                        visible,
                                                                        icon,
                                                                        labelElement,
                                                                    } =
                                                                        PLATFORM_SECTION_MENU_ITEMS[
                                                                            key
                                                                        ];
                                                                    if (
                                                                        visible
                                                                    ) {
                                                                        return (
                                                                            <MenuItem
                                                                                key={
                                                                                    key
                                                                                }
                                                                                text={
                                                                                    text
                                                                                }
                                                                                labelElement={
                                                                                    labelElement
                                                                                }
                                                                                icon={
                                                                                    <FAIcon
                                                                                        icon={
                                                                                            icon
                                                                                        }
                                                                                    />
                                                                                }
                                                                                onClick={() => {
                                                                                    addContainer(
                                                                                        {
                                                                                            icon,
                                                                                            title,
                                                                                            content,
                                                                                        }
                                                                                    );
                                                                                }}
                                                                            />
                                                                        );
                                                                    }
                                                                    return null;
                                                                })}
                                                            </>
                                                        )}
                                                    </Menu>
                                                </div>
                                            )}
                                        </div>
                                    </Card>
                                )}
                            </ExpandingBox>
                        </div>
                        <Alert
                            isOpen={userProfileError}
                            intent={Intent.DANGER}
                            confirmButtonText="Sign out"
                            onConfirm={logout}
                        >
                            There seems to be an issue with your account
                            information. Please log in again to continue.
                        </Alert>
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

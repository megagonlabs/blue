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
    Tag,
} from "@blueprintjs/core";
import { Omnibar } from "@blueprintjs/select";
import {
    faBellConcierge,
    faCircleA,
    faInboxFull,
    faInboxOut,
    faMagnifyingGlass,
    faPencilRuler,
    faScrewdriverWrench,
    faUserGroup,
    faWavePulse,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import { motion } from "framer-motion";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import Image from "next/image";
import { useEffect } from "react";
import { useShallow } from "zustand/react/shallow";
import AccountPanel from "./AccountPanel";
import Authentication from "./Authentication";
import { CIRCLE_DOT_WITH_FADE, ENTITY_TYPE_LOOKUP } from "./constants";
import ExpandingBox from "./ExpandingBox";
import { FAIcon } from "./FAIcon";
import Dock from "./navigation/Dock";
import TopSessions from "./navigation/TopSessions";
import WSConnectionIndicator from "./navigation/WSConnectionIndicator";
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
import ApplicationContainer from "./sessions/ApplicationContainer";
import SessionList from "./sessions/SessionList";
import FormDesigner from "./tools/FormDesigner";
import UITour from "./ux/UITour";
import VerticalScrollable from "./VerticalScrollable";
const { NEXT_PUBLIC_PLATFORM_NAME } = allEnv();
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
            disabled: true,
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
    const addApplicationContainer = () => {
        addContainer({
            icon: AGENT_GROUP_ICON,
            title: "Applications",
            content: <ApplicationContainer />,
            uniqueId: `ApplicationContainer`,
        });
    };
    useEffect(() => {
        addApplicationContainer();
    }, []);
    const { createNewSession } = useSessionStore(
        useShallow((state) => ({
            createNewSession: state.createNewSession,
        }))
    );
    const userProfileError =
        !_.isEmpty(user) && _.isEmpty(_.get(user, "role", null));
    const PLATFORM_SECTION_MENU_ITEMS = {
        systemStatus: {
            title: "System Status",
            text: "System Status",
            icon: faWavePulse,
            content: <SystemStatusContainer />,
            visible: permissions.canReadPlatformStatus,
            labelElement: isSystemStatusLive && CIRCLE_DOT_WITH_FADE,
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
            icon: faBellConcierge,
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
                            id="platform-onboarding-tour-user-settings"
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
                                expandedWidth={370}
                                expandedHeight={141.43}
                            >
                                {(isExpanded) => (
                                    <AccountPanel isExpanded={isExpanded} />
                                )}
                            </ExpandingBox>
                        </div>
                        <div
                            id="platform-onboarding-tour-navigation-menu"
                            style={{
                                position: "absolute",
                                top: 20,
                                left: 20,
                                zIndex: 19,
                            }}
                        >
                            <ExpandingBox
                                transitionDuration={0}
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
                                            padding: 0,
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
                                            {isExpanded && (
                                                <motion.div
                                                    initial="hidden"
                                                    animate="visible"
                                                    variants={{
                                                        hidden: { opacity: 0 },
                                                        visible: { opacity: 1 },
                                                    }}
                                                    exit="hidden"
                                                    transition={{
                                                        duration: 0.3,
                                                        ease: "easeIn",
                                                    }}
                                                    style={{
                                                        position: "absolute",
                                                        right: 20,
                                                        top: 20,
                                                        zIndex: 2,
                                                    }}
                                                >
                                                    <Tag
                                                        style={{
                                                            maxWidth: 120,
                                                            lineHeight: "21px",
                                                        }}
                                                        intent={Intent.PRIMARY}
                                                        minimal
                                                    >
                                                        {
                                                            NEXT_PUBLIC_PLATFORM_NAME
                                                        }
                                                    </Tag>
                                                </motion.div>
                                            )}
                                            <VerticalScrollable
                                                showTopIndicator={false}
                                                showBottomIndicator={isExpanded}
                                                transitionDuration={150}
                                                backgroundColor={
                                                    darkMode
                                                        ? Colors.DARK_GRAY2
                                                        : Colors.WHITE
                                                }
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
                                                        src="/images/logo.svg"
                                                        alt="Megagon Labs logo"
                                                    />
                                                    <div
                                                        className="full-parent-width"
                                                        style={{
                                                            background: darkMode
                                                                ? "linear-gradient(to bottom, rgba(37,42,49,1) 0%, rgba(37,42,49,1) 65px, rgba(255,255,255,0) 99%, rgba(255,255,255,0) 100%)"
                                                                : "linear-gradient(to bottom, rgba(255,255,255,1) 0%, rgba(255,255,255,1) 65px, rgba(255,255,255,0) 99%, rgba(255,255,255,0) 100%)",
                                                            height: 85,
                                                            position:
                                                                "absolute",
                                                            borderTopLeftRadius: 10,
                                                            borderTopRightRadius: 10,
                                                            width: "calc(100% + 40px)",
                                                            top: -20,
                                                            left: -20,
                                                        }}
                                                    />
                                                </div>
                                                {isExpanded && (
                                                    <div
                                                        style={{
                                                            marginTop: 30,
                                                        }}
                                                    >
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
                                                                    text="Applications"
                                                                    onClick={
                                                                        addApplicationContainer
                                                                    }
                                                                />
                                                            )}
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
                                                                                    icon: faInboxFull,
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
                                                                            onClick={() => {
                                                                                createNewSession(
                                                                                    {}
                                                                                );
                                                                            }}
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
                                                                    <MenuDivider title="Registries" />
                                                                    {[
                                                                        "agent",
                                                                        "source",
                                                                        "operator",
                                                                        "model",
                                                                        "server",
                                                                    ].map(
                                                                        (
                                                                            type
                                                                        ) => {
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
                                                                                        icon: faPencilRuler,
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
                                                                    ].map(
                                                                        (
                                                                            key
                                                                        ) => {
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
                                                                        }
                                                                    )}
                                                                </>
                                                            )}
                                                        </Menu>
                                                    </div>
                                                )}
                                            </VerticalScrollable>
                                        </div>
                                    </Card>
                                )}
                            </ExpandingBox>
                        </div>
                        <div
                            className="scrollbar-none"
                            style={{
                                position: "absolute",
                                top: 85,
                                left: 20,
                                width: 65,
                                height: "calc(100% - 170px)",
                                overflowY: "auto",
                            }}
                        >
                            <VerticalScrollable
                                caretPaddingBottom={20}
                                caretPaddingTop={20}
                                backgroundColor={
                                    darkMode
                                        ? Colors.DARK_GRAY1
                                        : Colors.LIGHT_GRAY5
                                }
                            >
                                <div style={{ padding: "21px 0px" }}>
                                    <UITour />
                                    <WSConnectionIndicator />
                                    <TopSessions />
                                    <Dock />
                                </div>
                            </VerticalScrollable>
                        </div>
                        <Alert
                            isOpen={userProfileError}
                            intent={Intent.DANGER}
                            confirmButtonText="Sign out"
                            onConfirm={logout}
                        >
                            There seems to be an issue with your account
                            information. Please sign in again to continue.
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

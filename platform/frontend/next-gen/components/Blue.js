import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useSessionStore } from "@/stores/session-store";
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
import { ENTITY_TYPE_CONVERSION, ENTITY_TYPE_LOOKUP } from "./constants";
import ExpandingBox from "./ExpandingBox";
import { FAIcon } from "./FAIcon";
import PlatformConfigurations from "./platforms/PlatformConfigurations";
import PlatformUsers from "./platforms/PlatformUsers";
import SystemStatusContainer from "./platforms/SystemStatusContainer";
import AgentList from "./registries/agents/AgentList";
import SourceList from "./registries/data/SourceList";
import ModelList from "./registries/models/ModelList";
import OperatorList from "./registries/operators/OperatorList";
import SessionList from "./sessions/SessionList";
import FormDesigner from "./tools/FormDesigner";
const REGISTRY_MENU_ITEMS = {
    agent: { title: "Agent Registry", text: "Agent", content: <AgentList /> },
    source: { title: "Data Registry", text: "Data", content: <SourceList /> },
    operator: {
        title: "Operator Registry",
        text: "Operator",
        content: <OperatorList />,
    },
    model: { title: "Model Registry", text: "Model", content: <ModelList /> },
};
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
    const createNewSession = useSessionStore((state) => state.createNewSession);
    const userProfileError =
        !_.isEmpty(user) && _.isEmpty(_.get(user, "role", null));
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
                                                    ]) && (
                                                        <>
                                                            <MenuDivider title="Registries" />
                                                            {[
                                                                "agent",
                                                                "source",
                                                                "operator",
                                                                "model",
                                                            ].map((type) => {
                                                                const {
                                                                    title,
                                                                    text,
                                                                    content,
                                                                } =
                                                                    REGISTRY_MENU_ITEMS[
                                                                        type
                                                                    ];
                                                                const { icon } =
                                                                    ENTITY_TYPE_LOOKUP[
                                                                        type
                                                                    ];
                                                                return (
                                                                    permissions[
                                                                        `canRead${_.capitalize(
                                                                            _.get(
                                                                                ENTITY_TYPE_CONVERSION,
                                                                                type,
                                                                                type
                                                                            )
                                                                        )}Registry`
                                                                    ] && (
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
                                                            })}
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
                                                            {permissions.canReadPlatformStatus && (
                                                                <MenuItem
                                                                    onClick={() =>
                                                                        addContainer(
                                                                            {
                                                                                title: "System Status",
                                                                                content:
                                                                                    (
                                                                                        <SystemStatusContainer />
                                                                                    ),
                                                                            }
                                                                        )
                                                                    }
                                                                    text="System Status"
                                                                    icon={
                                                                        <FAIcon
                                                                            icon={
                                                                                faWavePulse
                                                                            }
                                                                        />
                                                                    }
                                                                />
                                                            )}
                                                            {permissions.canReadPlatformAgents && (
                                                                <MenuItem
                                                                    text="Agents"
                                                                    icon={
                                                                        <FAIcon
                                                                            icon={
                                                                                faCircleA
                                                                            }
                                                                        />
                                                                    }
                                                                />
                                                            )}
                                                            {permissions.canReadPlatformServices && (
                                                                <MenuItem
                                                                    text="Services"
                                                                    icon={
                                                                        <FAIcon
                                                                            icon={
                                                                                faLayerGroup
                                                                            }
                                                                        />
                                                                    }
                                                                />
                                                            )}
                                                            {permissions.canWritePlatformUsers && (
                                                                <MenuItem
                                                                    onClick={() =>
                                                                        addContainer(
                                                                            {
                                                                                icon: faUserGroup,
                                                                                title: "Platform Users",
                                                                                content:
                                                                                    (
                                                                                        <PlatformUsers />
                                                                                    ),
                                                                            }
                                                                        )
                                                                    }
                                                                    text="Users"
                                                                    icon={
                                                                        <FAIcon
                                                                            icon={
                                                                                faUserGroup
                                                                            }
                                                                        />
                                                                    }
                                                                />
                                                            )}
                                                            {permissions.canWritePlatformSettings && (
                                                                <MenuItem
                                                                    onClick={() =>
                                                                        addContainer(
                                                                            {
                                                                                icon: faScrewdriverWrench,
                                                                                title: "Platform Configurations",
                                                                                content:
                                                                                    (
                                                                                        <PlatformConfigurations />
                                                                                    ),
                                                                            }
                                                                        )
                                                                    }
                                                                    text="Configurations"
                                                                    icon={
                                                                        <FAIcon
                                                                            icon={
                                                                                faScrewdriverWrench
                                                                            }
                                                                        />
                                                                    }
                                                                />
                                                            )}
                                                        </>
                                                    )}
                                                </Menu>
                                            </div>
                                        )}
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

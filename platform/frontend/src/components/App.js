import AccessDeniedNonIdealState from "@/components/AccessDeniedNonIdealState";
import {
    ENTITY_TYPE_LOOKUP,
    NAVIGATION_MENU_WIDTH,
} from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import { useSocket } from "@/components/hooks/useSocket";
import { faIcon } from "@/components/icon";
import {
    Alignment,
    Button,
    ButtonGroup,
    Card,
    Classes,
    Colors,
    Divider,
    H3,
    Intent,
    MenuDivider,
    Navbar,
    NavbarHeading,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { faCircleSmall as faCircleSmallSolid } from "@fortawesome/pro-solid-svg-icons";
import {
    fa1,
    fa2,
    fa3,
    fa4,
    fa5,
    faCircleSmall,
    faHashtag,
    faInboxArrowUp,
    faInboxFull,
    faLayerGroup,
    faPencilRuler,
    faRectangleTerminal,
    faScrewdriverWrench,
    faSlidersSimple,
    faUserGroup,
    faWavePulse,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext, useMemo, useState } from "react";
import DebugPanel from "./debugger/DebugPanel";
import { hasTrue, populateRouterPathname } from "./helper";
import Settings from "./navigation/Settings";
import UserAccountPanel from "./navigation/UserAccountPanel";
const {
    NEXT_PUBLIC_DATA_REGISTRY_NAME,
    NEXT_PUBLIC_AGENT_REGISTRY_NAME,
    NEXT_PUBLIC_OPERATOR_REGISTRY_NAME,
    NEXT_PUBLIC_MODEL_REGISTRY_NAME,
    NEXT_PUBLIC_PLATFORM_NAME,
} = allEnv();
export default function App({ children }) {
    const router = useRouter();
    const { appState, appActions } = useContext(AppContext);
    const { sessionDetails, creatingSession, sessionIds, unreadSessionIds } =
        appState.session;
    const { isSocketOpen } = useSocket();
    const recentSessions = useMemo(
        () =>
            _.intersection(
                Object.values(sessionDetails)
                    .filter((session) =>
                        _.get(session, "group_by.owner", false)
                    )
                    .sort((a, b) => b.created_date - a.created_date)
                    .map((session) => session.id),
                sessionIds
            ).slice(0, 5),
        [sessionDetails, sessionIds]
    );
    const { user, permissions, settings } = useContext(AuthContext);
    const userRole = _.get(user, "role", null);
    const compactSidebar = _.get(settings, "compact_sidebar", false);
    const darkMode = _.get(settings, "dark_mode", false);
    const sidebarWidth = compactSidebar ? 80 : NAVIGATION_MENU_WIDTH;
    const {
        canWritePlatformUsers,
        canReadPlatformServices,
        showFormDesigner,
        showPromptDesigner,
        canReadPlatformAgents,
        canReadSessions,
        canReadDataRegistry,
        canReadAgentRegistry,
        canReadOperatorRegistry,
        canReadModelRegistry,
        showRegistryList,
        launchScreen,
    } = permissions;
    const launchScreenMode = launchScreen && _.isEqual(router.pathname, "/");
    const MENU_ITEMS = {
        all_sessions: {
            href: "/sessions",
            text: "Sessions",
            icon: faInboxFull,
            visible: canReadSessions,
        },
        data_registry: {
            href: `/registry/${NEXT_PUBLIC_DATA_REGISTRY_NAME}/data`,
            text: "Data",
            icon: ENTITY_TYPE_LOOKUP.source.icon,
            visible: canReadDataRegistry,
        },
        agent_registry: {
            href: `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent`,
            text: "Agent",
            icon: ENTITY_TYPE_LOOKUP.agent.icon,
            visible: canReadAgentRegistry,
        },
        operator_registry: {
            href: `/registry/${NEXT_PUBLIC_OPERATOR_REGISTRY_NAME}/operator`,
            text: "Operator",
            icon: ENTITY_TYPE_LOOKUP.operator.icon,
            visible: canReadOperatorRegistry,
        },
        model_registry: {
            href: `/registry/${NEXT_PUBLIC_MODEL_REGISTRY_NAME}/model`,
            text: "Model",
            icon: ENTITY_TYPE_LOOKUP.model.icon,
            visible: canReadModelRegistry,
        },
        form_designer: {
            href: "/tools/form-designer",
            text: "Form Designer",
            icon: faPencilRuler,
            visible: showFormDesigner,
        },
        prompt_designer: {
            href: "/tools/prompt-designer",
            text: "Auto Prompt",
            icon: faRectangleTerminal,
            visible: showPromptDesigner,
        },
        admin_users: {
            href: "/admin/users",
            text: "Users",
            icon: faUserGroup,
            visible: canWritePlatformUsers,
        },
        admin_services: {
            href: "/admin/services",
            text: "Services",
            icon: faLayerGroup,
            visible: canReadPlatformServices,
        },
        admin_agents: {
            href: "/admin/agents",
            text: "Agents",
            icon: ENTITY_TYPE_LOOKUP.agent.icon,
            visible: canReadPlatformAgents,
        },
        admin_status: {
            href: "/admin/status",
            text: "Status",
            icon: faWavePulse,
            visible: _.isEqual(userRole, "admin"),
        },
        admin_configurations: {
            href: "/admin/configs",
            text: "Configs",
            icon: faScrewdriverWrench,
            visible: _.isEqual(userRole, "admin"),
        },
    };
    const NUMBER_TO_ICON = {
        1: fa1,
        2: fa2,
        3: fa3,
        4: fa4,
        5: fa5,
    };
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const RIGHT_HAND_ACTIONS = [
        {
            content: "Settings",
            icon: faSlidersSimple,
            onClick: () => setIsSettingsOpen(true),
        },
    ];
    return (
        <div className={darkMode ? Classes.DARK : null}>
            <Navbar style={{ paddingLeft: 20, paddingRight: 20 }}>
                <Navbar.Group align={Alignment.START}>
                    <Image
                        width={25}
                        height={25}
                        src="/images/logo.png"
                        alt="Megagon Labs logo"
                    />
                    <Link className="no-link-decoration" href="/">
                        <NavbarHeading style={{ display: "flex" }}>
                            <H3 style={{ margin: "0px 10px 0px" }}>Blue</H3>
                            <Tag minimal intent={Intent.PRIMARY}>
                                {NEXT_PUBLIC_PLATFORM_NAME}
                            </Tag>
                        </NavbarHeading>
                    </Link>
                </Navbar.Group>
                <Navbar.Group align={Alignment.END}>
                    {RIGHT_HAND_ACTIONS.map((action, index) => (
                        <Tooltip
                            placement="bottom"
                            minimal
                            key={index}
                            content={action.content}
                            openOnTargetFocus={false}
                        >
                            <Button
                                size="large"
                                variant="minimal"
                                onClick={action.onClick}
                                icon={faIcon({ icon: action.icon })}
                            />
                        </Tooltip>
                    ))}
                    <UserAccountPanel />
                </Navbar.Group>
            </Navbar>
            <Settings
                isOpen={isSettingsOpen}
                setIsSettingsOpen={setIsSettingsOpen}
            />
            {launchScreenMode || _.isEmpty(user) ? null : (
                <Card
                    interactive
                    style={{
                        position: "absolute",
                        top: 50,
                        left: 0,
                        height: "calc(100vh - 50px)",
                        width: sidebarWidth,
                        borderRadius: 0,
                        display: "flex",
                        flexDirection: "column",
                        zIndex: 2,
                        padding: 20,
                        overflowY: "auto",
                    }}
                >
                    {hasTrue([canReadSessions]) ? (
                        <>
                            {!compactSidebar && (
                                <MenuDivider title="Sessions" />
                            )}
                            <ButtonGroup
                                alignText={Alignment.START}
                                vertical
                                variant="minimal"
                                className="full-parent-width"
                            >
                                {canReadSessions &&
                                    recentSessions.map((sessionId, index) => {
                                        let sessionDisplayName = _.get(
                                            sessionDetails,
                                            [sessionId, "name"],
                                            sessionId
                                        );
                                        if (
                                            _.isEqual(
                                                sessionDisplayName,
                                                sessionId
                                            )
                                        ) {
                                            const utcSeconds = _.get(
                                                sessionDetails,
                                                [sessionId, "created_date"],
                                                0
                                            );
                                            let date = new Date(0); // The 0 here sets the date to the epoch
                                            date.setUTCSeconds(utcSeconds);
                                            sessionDisplayName =
                                                date.toLocaleString();
                                        }
                                        const buttonText = (
                                            <div
                                                style={{
                                                    maxWidth: compactSidebar
                                                        ? 200
                                                        : 133,
                                                }}
                                                className={
                                                    Classes.TEXT_OVERFLOW_ELLIPSIS
                                                }
                                            >
                                                #&nbsp;
                                                {sessionDisplayName}
                                            </div>
                                        );
                                        return (
                                            <Tooltip
                                                key={sessionId}
                                                minimal
                                                placement="right"
                                                content={
                                                    compactSidebar
                                                        ? buttonText
                                                        : null
                                                }
                                            >
                                                <Button
                                                    icon={
                                                        compactSidebar &&
                                                        faIcon({
                                                            icon: _.get(
                                                                NUMBER_TO_ICON,
                                                                index + 1,
                                                                faHashtag
                                                            ),
                                                        })
                                                    }
                                                    style={{
                                                        padding: "5px 15px",
                                                    }}
                                                    onClick={() => {
                                                        if (!router.isReady)
                                                            return;
                                                        router.push(
                                                            `/sessions/${sessionId}`
                                                        );
                                                    }}
                                                    text={
                                                        !compactSidebar &&
                                                        buttonText
                                                    }
                                                />
                                            </Tooltip>
                                        );
                                    })}
                                {["all_sessions"].map((key, index) => {
                                    const {
                                        href,
                                        icon,
                                        text,
                                        visible,
                                        onClick,
                                        disabled,
                                        intent,
                                    } = _.get(MENU_ITEMS, key, {});
                                    if (!visible) {
                                        return null;
                                    }
                                    const active = _.startsWith(
                                            router.pathname,
                                            href
                                        ),
                                        showUnreadIndicator =
                                            _.isEqual(key, "all_sessions") &&
                                            !_.isEmpty(unreadSessionIds);
                                    return (
                                        <Link
                                            className="no-link-decoration"
                                            href={href}
                                            key={index}
                                            style={{ position: "relative" }}
                                        >
                                            <Tooltip
                                                minimal
                                                placement="right"
                                                content={
                                                    compactSidebar ? text : null
                                                }
                                            >
                                                <Button
                                                    intent={intent}
                                                    size="large"
                                                    style={
                                                        !active
                                                            ? {
                                                                  backgroundColor:
                                                                      "transparent",
                                                              }
                                                            : null
                                                    }
                                                    active={active}
                                                    text={
                                                        !compactSidebar && text
                                                    }
                                                    disabled={disabled}
                                                    icon={faIcon({
                                                        icon: icon,
                                                    })}
                                                    onClick={onClick}
                                                    endIcon={
                                                        !compactSidebar &&
                                                        showUnreadIndicator &&
                                                        faIcon({
                                                            icon: faCircleSmall,
                                                            style: {
                                                                color: Colors.RED3,
                                                            },
                                                        })
                                                    }
                                                />
                                            </Tooltip>
                                            {compactSidebar &&
                                                showUnreadIndicator && (
                                                    <div
                                                        style={{
                                                            position:
                                                                "absolute",
                                                            right: 5,
                                                            top: 5,
                                                            zIndex: 7,
                                                        }}
                                                    >
                                                        {faIcon({
                                                            icon: faCircleSmallSolid,
                                                            style: {
                                                                color: Colors.RED3,
                                                            },
                                                        })}
                                                    </div>
                                                )}
                                        </Link>
                                    );
                                })}
                                <Tooltip
                                    minimal
                                    placement="right"
                                    content={
                                        compactSidebar ? "New Session" : null
                                    }
                                >
                                    <Button
                                        intent={Intent.PRIMARY}
                                        size="large"
                                        text={!compactSidebar && "New Session"}
                                        disabled={
                                            creatingSession || !isSocketOpen
                                        }
                                        icon={faIcon({ icon: faInboxArrowUp })}
                                        onClick={() => {
                                            if (
                                                !isSocketOpen ||
                                                !router.isReady
                                            )
                                                return;
                                            appActions.session.createSession({
                                                router,
                                            });
                                        }}
                                    />
                                </Tooltip>
                            </ButtonGroup>
                        </>
                    ) : null}
                    {hasTrue([
                        canReadAgentRegistry,
                        canReadDataRegistry,
                        canReadOperatorRegistry,
                        canReadModelRegistry,
                    ]) && showRegistryList ? (
                        <>
                            <div>&nbsp;</div>
                            {compactSidebar ? (
                                <Divider
                                    style={{ marginBottom: 18, marginTop: 0 }}
                                />
                            ) : (
                                <MenuDivider title="Registries" />
                            )}
                            <ButtonGroup
                                alignText={Alignment.START}
                                vertical
                                variant="minimal"
                                size="large"
                                className="full-parent-width"
                            >
                                {[
                                    "agent_registry",
                                    "data_registry",
                                    // "operator_registry",
                                    // "model_registry",
                                ].map((key, index) => {
                                    const { href, icon, text, visible } = _.get(
                                        MENU_ITEMS,
                                        key,
                                        {}
                                    );
                                    if (!visible) {
                                        return null;
                                    }
                                    const active = _.startsWith(
                                        populateRouterPathname(router),
                                        href
                                    );
                                    return (
                                        <Link
                                            className="no-link-decoration"
                                            href={href}
                                            key={index}
                                        >
                                            <Tooltip
                                                minimal
                                                placement="right"
                                                content={
                                                    compactSidebar ? text : null
                                                }
                                            >
                                                <Button
                                                    style={
                                                        !active
                                                            ? {
                                                                  backgroundColor:
                                                                      "transparent",
                                                              }
                                                            : null
                                                    }
                                                    active={active}
                                                    text={
                                                        !compactSidebar && text
                                                    }
                                                    icon={faIcon({
                                                        icon: icon,
                                                    })}
                                                />
                                            </Tooltip>
                                        </Link>
                                    );
                                })}
                            </ButtonGroup>
                        </>
                    ) : null}
                    {hasTrue([showFormDesigner, showPromptDesigner]) ? (
                        <>
                            <div>&nbsp;</div>
                            {compactSidebar ? (
                                <Divider
                                    style={{ marginBottom: 18, marginTop: 0 }}
                                />
                            ) : (
                                <MenuDivider title="Dev. Tools" />
                            )}
                            <ButtonGroup
                                alignText={Alignment.START}
                                vertical
                                variant="minimal"
                                size="large"
                                className="full-parent-width"
                            >
                                {["form_designer"].map((key, index) => {
                                    const { href, icon, text, visible } = _.get(
                                        MENU_ITEMS,
                                        key,
                                        {}
                                    );
                                    if (!visible) {
                                        return null;
                                    }
                                    const active = _.startsWith(
                                        router.pathname,
                                        href
                                    );
                                    return (
                                        <Link
                                            className="no-link-decoration"
                                            href={href}
                                            key={index}
                                        >
                                            <Tooltip
                                                minimal
                                                placement="right"
                                                content={
                                                    compactSidebar ? text : null
                                                }
                                            >
                                                <Button
                                                    style={
                                                        !active
                                                            ? {
                                                                  backgroundColor:
                                                                      "transparent",
                                                              }
                                                            : null
                                                    }
                                                    active={active}
                                                    text={
                                                        !compactSidebar && text
                                                    }
                                                    icon={faIcon({
                                                        icon: icon,
                                                    })}
                                                />
                                            </Tooltip>
                                        </Link>
                                    );
                                })}
                            </ButtonGroup>
                        </>
                    ) : null}
                    {hasTrue([
                        canReadPlatformAgents,
                        canWritePlatformUsers,
                        canReadPlatformServices,
                    ]) ? (
                        <>
                            <div>&nbsp;</div>
                            {compactSidebar ? (
                                <Divider
                                    style={{ marginBottom: 18, marginTop: 0 }}
                                />
                            ) : (
                                <MenuDivider title="Admin. Tools" />
                            )}
                            <ButtonGroup
                                alignText={Alignment.START}
                                vertical
                                variant="minimal"
                                size="large"
                                className="full-parent-width"
                            >
                                {[
                                    "admin_status",
                                    "admin_agents",
                                    "admin_services",
                                    "admin_users",
                                    "admin_configurations",
                                ].map((key, index) => {
                                    const { href, icon, text, visible } = _.get(
                                        MENU_ITEMS,
                                        key,
                                        {}
                                    );
                                    if (!visible) return null;
                                    const active = _.startsWith(
                                        router.pathname,
                                        href
                                    );
                                    return (
                                        <Link
                                            className="no-link-decoration"
                                            href={href}
                                            key={index}
                                        >
                                            <Tooltip
                                                minimal
                                                placement="right"
                                                content={
                                                    compactSidebar ? text : null
                                                }
                                            >
                                                <Button
                                                    style={
                                                        !active
                                                            ? {
                                                                  backgroundColor:
                                                                      "transparent",
                                                              }
                                                            : null
                                                    }
                                                    active={active}
                                                    text={
                                                        !compactSidebar && text
                                                    }
                                                    icon={faIcon({
                                                        icon: icon,
                                                    })}
                                                />
                                            </Tooltip>
                                        </Link>
                                    );
                                })}
                            </ButtonGroup>
                        </>
                    ) : null}
                </Card>
            )}
            <div
                style={{
                    marginLeft:
                        !launchScreenMode && !_.isEmpty(user)
                            ? sidebarWidth
                            : null,
                    height: "calc(100vh - 50px)",
                    position: "relative",
                    backgroundColor: darkMode
                        ? Colors.DARK_GRAY1
                        : Colors.LIGHT_GRAY5,
                }}
            >
                {_.isEmpty(user) ? <AccessDeniedNonIdealState /> : children}
            </div>
            {!_.isEmpty(user) && _.isEmpty(_.get(user, "role", null)) ? null : (
                <DebugPanel />
            )}
        </div>
    );
}

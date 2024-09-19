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
    H3,
    Intent,
    MenuDivider,
    Navbar,
    NavbarHeading,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faGear,
    faInboxArrowUp,
    faLayerGroup,
    faPencilRuler,
    faSquareTerminal,
    faUser,
    faUserGroup,
} from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext, useEffect, useMemo, useState } from "react";
import DebugPanel from "./debugger/DebugPanel";
import { hasTrue } from "./helper";
import Settings from "./navigation/Settings";
import UserAccountPanel from "./navigation/UserAccountPanel";
export default function App({ children }) {
    const router = useRouter();
    const { appState, appActions } = useContext(AppContext);
    const sessionDetails = appState.session.sessionDetails;
    const sessionIdFocus = appState.session.sessionIdFocus;
    const { socket, isSocketOpen } = useSocket();
    const recentSessions = useMemo(
        () =>
            Object.values(sessionDetails)
                .filter((session) => _.get(session, "group_by.owner", false))
                .sort((a, b) => b.created_date - a.created_date)
                .slice(0, 5)
                .map((session) => session.id),
        [sessionDetails]
    );
    const { user, permissions } = useContext(AuthContext);
    const {
        canWritePlatformUsers,
        canReadPlatformServices,
        showFormDesigner,
        showPromptDesigner,
        canReadPlatformAgents,
        canReadSessions,
        canReadDataRegistry,
        canWriteSessions,
        canReadAgentRegistry,
        canReadOperatorRegistry,
        canReadModelRegistry,
    } = permissions;
    const [isCreatingSession, setIsCreatingSession] = useState(false);
    const MENU_ITEMS = {
        my_sessions: {
            href: `/sessions`,
            text: "My Sessions",
            icon: faUser,
            visible: canReadDataRegistry,
            onClick: () => {
                appActions.session.setState({
                    key: "sessionGroupBy",
                    value: "owner",
                });
            },
        },
        new_session: {
            href: `/sessions`,
            text: "New Session",
            icon: faInboxArrowUp,
            visible: canWriteSessions,
            disabled: !isSocketOpen,
            intent: Intent.PRIMARY,
            onClick: () => {
                if (!isSocketOpen) {
                    return;
                }
                setIsCreatingSession(true);
                appActions.session.createSession(socket);
            },
        },
        data_registry: {
            href: `/registry/${process.env.NEXT_PUBLIC_DATA_REGISTRY_NAME}/data`,
            text: "Data",
            icon: ENTITY_TYPE_LOOKUP.source.icon,
            visible: canReadDataRegistry,
        },
        agent_registry: {
            href: `/registry/${process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent`,
            text: "Agent",
            icon: ENTITY_TYPE_LOOKUP.agent.icon,
            visible: canReadAgentRegistry,
        },
        operator_registry: {
            href: `/registry/${process.env.NEXT_PUBLIC_OPERATOR_REGISTRY_NAME}/operator`,
            text: "Operator",
            icon: ENTITY_TYPE_LOOKUP.operator.icon,
            visible: canReadOperatorRegistry,
        },
        model_registry: {
            href: `/registry/${process.env.NEXT_PUBLIC_MODEL_REGISTRY_NAME}/model`,
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
            icon: faSquareTerminal,
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
    };
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    useEffect(() => {
        if (appState.session.openAgentsDialogTrigger) {
            setIsCreatingSession(false);
        }
    }, [appState.session.openAgentsDialogTrigger]);
    return (
        <div>
            <Navbar style={{ paddingLeft: 20, paddingRight: 20 }}>
                <Navbar.Group align={Alignment.LEFT}>
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
                                {process.env.NEXT_PUBLIC_PLATFORM_NAME}
                            </Tag>
                        </NavbarHeading>
                    </Link>
                </Navbar.Group>
                <Navbar.Group align={Alignment.RIGHT}>
                    <Tooltip
                        placement="bottom"
                        minimal
                        content="Settings"
                        openOnTargetFocus={false}
                    >
                        <Button
                            onClick={() => {
                                setIsSettingsOpen(true);
                            }}
                            large
                            minimal
                            icon={faIcon({ icon: faGear })}
                        />
                    </Tooltip>
                    <UserAccountPanel />
                </Navbar.Group>
            </Navbar>
            <Settings
                isOpen={isSettingsOpen}
                setIsSettingsOpen={setIsSettingsOpen}
            />
            <Card
                interactive
                style={{
                    position: "absolute",
                    top: 50,
                    left: 0,
                    height: "calc(100vh - 50px)",
                    width: NAVIGATION_MENU_WIDTH,
                    borderRadius: 0,
                    display: "flex",
                    flexDirection: "column",
                    zIndex: 1,
                    padding: 20,
                    overflowY: "auto",
                }}
            >
                {hasTrue([canReadSessions]) ? (
                    <>
                        <MenuDivider title="Sessions" />
                        <ButtonGroup
                            alignText={Alignment.LEFT}
                            vertical
                            minimal
                            className="full-parent-width"
                        >
                            {canReadSessions &&
                                recentSessions.map((sessionId) => {
                                    const active =
                                        _.isEqual(sessionIdFocus, sessionId) &&
                                        _.startsWith(
                                            router.asPath,
                                            "/sessions"
                                        );
                                    return (
                                        <Button
                                            key={sessionId}
                                            active={active}
                                            style={{
                                                padding: "5px 15px",
                                                backgroundColor: !active
                                                    ? "transparent"
                                                    : null,
                                            }}
                                            onClick={() => {
                                                appActions.session.setSessionIdFocus(
                                                    sessionId
                                                );
                                                appActions.session.observeSession(
                                                    {
                                                        sessionId,
                                                        socket,
                                                    }
                                                );
                                                if (!router.isReady) {
                                                    return;
                                                }
                                                router.push("/sessions");
                                            }}
                                            text={
                                                <div
                                                    style={{ width: 133 }}
                                                    className={
                                                        Classes.TEXT_OVERFLOW_ELLIPSIS
                                                    }
                                                >
                                                    #{" "}
                                                    {_.get(
                                                        sessionDetails,
                                                        [sessionId, "name"],
                                                        sessionId
                                                    )}
                                                </div>
                                            }
                                        />
                                    );
                                })}
                            {["my_sessions", "new_session"].map(
                                (key, index) => {
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
                                    return (
                                        <Link href={href} key={index}>
                                            <Button
                                                intent={intent}
                                                large
                                                style={{
                                                    backgroundColor:
                                                        "transparent",
                                                }}
                                                text={text}
                                                disabled={disabled}
                                                icon={faIcon({ icon: icon })}
                                                onClick={onClick}
                                            />
                                        </Link>
                                    );
                                }
                            )}
                        </ButtonGroup>
                    </>
                ) : null}
                {hasTrue([
                    canReadAgentRegistry,
                    canReadDataRegistry,
                    canReadOperatorRegistry,
                ]) ? (
                    <>
                        <div>&nbsp;</div>
                        <MenuDivider title="Registries" />
                        <ButtonGroup
                            alignText={Alignment.LEFT}
                            vertical
                            minimal
                            large
                            className="full-parent-width"
                        >
                            {[
                                "agent_registry",
                                "data_registry",
                                "operator_registry",
                                "model_registry",
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
                                    router.asPath,
                                    href
                                );
                                return (
                                    <Link href={href} key={index}>
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
                                            text={text}
                                            icon={faIcon({
                                                icon: icon,
                                            })}
                                        />
                                    </Link>
                                );
                            })}
                        </ButtonGroup>
                    </>
                ) : null}
                {hasTrue([showFormDesigner]) ? (
                    <>
                        <div>&nbsp;</div>
                        <MenuDivider title="Dev. Tools" />
                        <ButtonGroup
                            alignText={Alignment.LEFT}
                            vertical
                            minimal
                            large
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
                                    router.asPath,
                                    href
                                );
                                return (
                                    <Link href={href} key={index}>
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
                                            text={text}
                                            icon={faIcon({
                                                icon: icon,
                                            })}
                                        />
                                    </Link>
                                );
                            })}
                        </ButtonGroup>
                    </>
                ) : null}
                {hasTrue([showPromptDesigner]) ? (
                    <>
                        <ButtonGroup
                            alignText={Alignment.LEFT}
                            vertical
                            minimal
                            large
                            className="full-parent-width"
                        >
                            {["prompt_designer"].map((key, index) => {
                                const { href, icon, text, visible } = _.get(
                                    MENU_ITEMS,
                                    key,
                                    {}
                                );
                                if (!visible) {
                                    return null;
                                }
                                const active = _.startsWith(
                                    router.asPath,
                                    href
                                );
                                return (
                                    <Link href={href} key={index}>
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
                                            text={text}
                                            icon={faIcon({
                                                icon: icon,
                                            })}
                                        />
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
                        <MenuDivider title="Admin. Tools" />
                        <ButtonGroup
                            alignText={Alignment.LEFT}
                            vertical
                            minimal
                            large
                            className="full-parent-width"
                        >
                            {[
                                "admin_services",
                                "admin_agents",
                                "admin_users",
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
                                    router.asPath,
                                    href
                                );
                                return (
                                    <Link href={href} key={index}>
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
                                            text={text}
                                            icon={faIcon({
                                                icon: icon,
                                            })}
                                        />
                                    </Link>
                                );
                            })}
                        </ButtonGroup>
                    </>
                ) : null}
            </Card>
            <div
                style={{
                    marginLeft: NAVIGATION_MENU_WIDTH,
                    height: "calc(100vh - 50px)",
                    position: "relative",
                }}
            >
                {_.isEmpty(user) ? <AccessDeniedNonIdealState /> : children}
            </div>
            <DebugPanel />
        </div>
    );
}

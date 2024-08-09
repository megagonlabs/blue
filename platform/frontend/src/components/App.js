import AccessDeniedNonIdealState from "@/components/AccessDeniedNonIdealState";
import { NAVIGATION_MENU_WIDTH } from "@/components/constant";
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
    faCircleA,
    faDatabase,
    faGear,
    faListUl,
    faPencilRuler,
    faUserGroup,
} from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext, useMemo, useState } from "react";
import { hasTrue } from "./helper";
import DebugPanel from "./navigation/DebugPanel";
import Settings from "./navigation/Settings";
import UserAccountPanel from "./navigation/UserAccountPanel";
export default function App({ children }) {
    const router = useRouter();
    const { appState, appActions } = useContext(AppContext);
    const sessionDetail = appState.session.sessionDetail;
    const sessionIdFocus = appState.session.sessionIdFocus;
    const { socket } = useSocket();
    const recentSessions = useMemo(
        () =>
            Object.values(sessionDetail)
                .sort((a, b) => b.created_date - a.created_date)
                .slice(0, 5)
                .map((session) => session.id),
        [sessionDetail]
    );
    const { user, permissions } = useContext(AuthContext);
    const {
        canWritePlatformUsers,
        showFormDesigner,
        canReadPlatformAgents,
        canReadSessions,
        canReadDataRegistry,
        canReadAgentRegistry,
    } = permissions;
    const MENU_ITEMS = {
        sessions: {
            href: "/sessions",
            text: "See All",
            icon: faListUl,
            visible: canReadSessions,
        },
        data_registry: {
            href: `/registry/${process.env.NEXT_PUBLIC_DATA_REGISTRY_NAME}/data`,
            text: "Data",
            icon: faDatabase,
            visible: canReadDataRegistry,
        },
        agent_registry: {
            href: `/registry/${process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent`,
            text: "Agent",
            icon: faCircleA,
            visible: canReadAgentRegistry,
        },
        form_designer: {
            href: "/tools/form-designer",
            text: "Form Designer",
            icon: faPencilRuler,
            visible: showFormDesigner,
        },
        admin_users: {
            href: "/admin/users",
            text: "Users",
            icon: faUserGroup,
            visible: canWritePlatformUsers,
        },
        admin_agents: {
            href: "/admin/agents",
            text: "Agents",
            icon: faCircleA,
            visible: canReadPlatformAgents,
        },
    };
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
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
                    justifyContent: "space-between",
                    zIndex: 1,
                    padding: 0,
                }}
            >
                <div
                    style={{
                        overflowY: "auto",
                        padding: 20,
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
                                style={{ marginBottom: 20 }}
                            >
                                {canReadSessions &&
                                    recentSessions.map((sessionId) => {
                                        const active =
                                            _.isEqual(
                                                sessionIdFocus,
                                                sessionId
                                            ) &&
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
                                                            sessionDetail,
                                                            [sessionId, "name"],
                                                            sessionId
                                                        )}
                                                    </div>
                                                }
                                            />
                                        );
                                    })}
                                {["sessions"].map((key, index) => {
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
                                                large
                                                style={
                                                    !active
                                                        ? {
                                                              backgroundColor:
                                                                  "transparent",
                                                          }
                                                        : null
                                                }
                                                active={
                                                    active &&
                                                    !recentSessions.includes(
                                                        sessionIdFocus
                                                    )
                                                }
                                                text={text}
                                                icon={faIcon({ icon: icon })}
                                            />
                                        </Link>
                                    );
                                })}
                            </ButtonGroup>
                        </>
                    ) : null}
                    {hasTrue([canReadAgentRegistry, canReadDataRegistry]) ? (
                        <>
                            <MenuDivider title="Registries" />
                            <ButtonGroup
                                alignText={Alignment.LEFT}
                                vertical
                                minimal
                                large
                                className="full-parent-width"
                            >
                                {["agent_registry", "data_registry"].map(
                                    (key, index) => {
                                        const { href, icon, text, visible } =
                                            _.get(MENU_ITEMS, key, {});
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
                                    }
                                )}
                            </ButtonGroup>
                        </>
                    ) : null}
                </div>
                {hasTrue([
                    canReadPlatformAgents,
                    canWritePlatformUsers,
                    showFormDesigner,
                ]) ? (
                    <div className="bp-border-top" style={{ padding: 20 }}>
                        {hasTrue([showFormDesigner]) ? (
                            <>
                                <MenuDivider title="Dev. Tools" />
                                <ButtonGroup
                                    alignText={Alignment.LEFT}
                                    vertical
                                    minimal
                                    large
                                    className="full-parent-width"
                                >
                                    {["form_designer"].map((key, index) => {
                                        const { href, icon, text, visible } =
                                            _.get(MENU_ITEMS, key, {});
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
                                    {["admin_agents", "admin_users"].map(
                                        (key, index) => {
                                            const {
                                                href,
                                                icon,
                                                text,
                                                visible,
                                            } = _.get(MENU_ITEMS, key, {});
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
                                        }
                                    )}
                                </ButtonGroup>
                            </>
                        ) : null}
                    </div>
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

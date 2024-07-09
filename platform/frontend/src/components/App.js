import SupportDialog from "@/components/SupportDialog";
import {
    NAVIGATION_MENU_WIDTH,
    PROFILE_PICTURE_40,
    USER_ROLES_LOOKUP,
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
    Popover,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowRightFromBracket,
    faCircleA,
    faDatabase,
    faGear,
    faListUl,
    faPencilRuler,
    faQuestion,
    faUserGroup,
} from "@fortawesome/pro-duotone-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext, useMemo, useState } from "react";
export default function App({ children }) {
    const router = useRouter();
    const { appState, appActions } = useContext(AppContext);
    const sessionDetail = appState.session.sessionDetail;
    const sessionIdFocus = appState.session.sessionIdFocus;
    const { socket } = useSocket();
    const pinnedSessionIds = useMemo(
        () =>
            Object.values(sessionDetail)
                .sort((a, b) => b.created_date - a.created_date)
                .slice(0, 5)
                .map((session) => session.id),
        [sessionDetail]
    );
    const { user, signOut } = useContext(AuthContext);
    const userRole = _.get(user, "role", null);
    const MENU_ITEMS = {
        sessions: {
            href: "/sessions",
            text: "See All",
            icon: faListUl,
        },
        data: {
            href: `/registry/${process.env.NEXT_PUBLIC_DATA_REGISTRY_NAME}/data`,
            text: "Data",
            icon: faDatabase,
        },
        agent: {
            href: `/registry/${process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent`,
            text: "Agent",
            icon: faCircleA,
        },
        designer: {
            href: "/tools/form-designer",
            text: "Form Designer",
            icon: faPencilRuler,
        },
        admin_users: {
            href: "/admin/users",
            text: "Users",
            icon: faUserGroup,
        },
        admin_agents: {
            href: "/admin/agents",
            text: "Agents",
            icon: faCircleA,
        },
        admin_services: {
            href: "/admin/services",
            text: "Services",
            icon: faGear,
        },
    };
    const [isSupportDialogOpen, setIsSupportDialogOpen] = useState(false);
    const openSupportDialog = () => {
        setIsSupportDialogOpen(true);
    };
    return (
        <div>
            <SupportDialog
                isOpen={isSupportDialogOpen}
                setIsSupportDialogOpen={setIsSupportDialogOpen}
            />
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
                {!_.isEmpty(user) ? (
                    <Navbar.Group align={Alignment.RIGHT}>
                        <Tooltip placement="bottom" minimal content="Support">
                            <Button
                                minimal
                                large
                                onClick={openSupportDialog}
                                icon={faIcon({ icon: faQuestion })}
                            />
                        </Tooltip>
                        <Popover
                            minimal
                            placement="bottom-end"
                            content={
                                <div
                                    className={Classes.RUNNING_TEXT}
                                    style={{
                                        padding: "20px 40px",
                                        textAlign: "center",
                                    }}
                                >
                                    <div style={{ fontWeight: 500 }}>
                                        {_.get(user, "email", "-")}
                                    </div>
                                    <div
                                        className={classNames(
                                            Classes.TEXT_MUTED,
                                            Classes.TEXT_SMALL
                                        )}
                                    >
                                        Managed by&nbsp;
                                        {_.get(user, "email_domain", "-")}
                                    </div>
                                    <div style={{ marginTop: 5 }}>
                                        <Tag minimal>
                                            {_.get(
                                                USER_ROLES_LOOKUP,
                                                userRole,
                                                userRole
                                            )}
                                        </Tag>
                                    </div>
                                    <Image
                                        alt=""
                                        src={_.get(user, "picture", "").replace(
                                            "=s96-c",
                                            "=s288-c"
                                        )}
                                        style={{
                                            marginTop: 20,
                                            borderRadius: "50%",
                                        }}
                                        width={80}
                                        height={80}
                                    />
                                    <div style={{ marginTop: 20 }}>
                                        <Button
                                            intent={Intent.WARNING}
                                            onClick={signOut}
                                            icon={faIcon({
                                                icon: faArrowRightFromBracket,
                                            })}
                                            text="Sign out"
                                            outlined
                                            large
                                        />
                                    </div>
                                </div>
                            }
                        >
                            <Tooltip
                                minimal
                                placement="bottom-end"
                                content={
                                    <div className={Classes.TEXT_MUTED}>
                                        {_.get(user, "name", null)}
                                        <br />
                                        {_.get(user, "email", null)}
                                    </div>
                                }
                            >
                                <Card
                                    interactive
                                    style={{
                                        ...PROFILE_PICTURE_40,
                                        marginLeft: 10,
                                        marginTop: 4,
                                    }}
                                >
                                    <Image
                                        alt=""
                                        src={_.get(user, "picture", "")}
                                        width={40}
                                        height={40}
                                    />
                                </Card>
                            </Tooltip>
                        </Popover>
                    </Navbar.Group>
                ) : null}
            </Navbar>
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
                    <MenuDivider title="Sessions" />
                    <ButtonGroup
                        alignText={Alignment.LEFT}
                        vertical
                        minimal
                        className="full-parent-width"
                        style={{ marginBottom: 20 }}
                    >
                        {pinnedSessionIds.map((sessionId) => (
                            <Button
                                key={sessionId}
                                active={
                                    _.isEqual(sessionIdFocus, sessionId) &&
                                    _.startsWith(router.asPath, "/sessions")
                                }
                                style={{ padding: "5px 15px" }}
                                onClick={() => {
                                    appActions.session.setSessionIdFocus(
                                        sessionId
                                    );
                                    appActions.session.observeSession({
                                        sessionId,
                                        socket,
                                    });
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
                        ))}
                        {["sessions"].map((key, index) => {
                            const { href, icon, text } = _.get(
                                MENU_ITEMS,
                                key,
                                {}
                            );
                            const active = _.startsWith(router.asPath, href);
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
                                            !pinnedSessionIds.includes(
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
                    <MenuDivider title="Registries" />
                    <ButtonGroup
                        alignText={Alignment.LEFT}
                        vertical
                        minimal
                        large
                        className="full-parent-width"
                    >
                        {["agent", "data"].map((key, index) => {
                            const { href, icon, text } = _.get(
                                MENU_ITEMS,
                                key,
                                {}
                            );
                            const active = _.startsWith(router.asPath, href);
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
                                        icon={faIcon({ icon: icon })}
                                    />
                                </Link>
                            );
                        })}
                    </ButtonGroup>
                </div>
                {_.includes(["admin", "developer"], userRole) ? (
                    <div className="bp-border-top" style={{ padding: 20 }}>
                        {_.includes(["admin", "developer"], userRole) ? (
                            <>
                                <MenuDivider title="Dev. Tools" />
                                <ButtonGroup
                                    alignText={Alignment.LEFT}
                                    vertical
                                    minimal
                                    large
                                    className="full-parent-width"
                                >
                                    {["designer"].map((key, index) => {
                                        const { href, icon, text } = _.get(
                                            MENU_ITEMS,
                                            key,
                                            {}
                                        );
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
                        {_.isEqual(userRole, "admin") ? (
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
                                        "admin_agents",
                                        "admin_services",
                                        "admin_users",
                                    ].map((key, index) => {
                                        const { href, icon, text } = _.get(
                                            MENU_ITEMS,
                                            key,
                                            {}
                                        );
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
                {children}
            </div>
        </div>
    );
}

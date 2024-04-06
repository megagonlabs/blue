import { AppContext } from "@/components/app-context";
import { connectToWebsocket } from "@/components/helper";
import { faIcon } from "@/components/icon";
import SessionList from "@/components/sessions/SessionList";
import SessionMessages from "@/components/sessions/SessionMessages";
import {
    Button,
    ButtonGroup,
    Card,
    Classes,
    H4,
    H5,
    InputGroup,
    Intent,
    Menu,
    MenuItem,
    NonIdealState,
    Popover,
    TextArea,
} from "@blueprintjs/core";
import {
    faCaretDown,
    faCirclePlus,
    faInboxIn,
    faInboxOut,
    faMessages,
    faSignalStreamSlash,
    faSquareDashedCirclePlus,
} from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useContext, useEffect, useRef, useState } from "react";
export default function Sessions() {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const sessionIds = appState.session.sessionIds;
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);
    const [joinSessionId, setJoinSessionId] = useState("");
    const sessionMessageTextArea = useRef(null);
    const sendSessionMessage = (message) => {
        if (_.isNil(appState.session.connection)) return;
        setMessage("");
        appState.session.connection.send(
            JSON.stringify({
                type: "USER_SESSION_MESSAGE",
                session_id: appState.session.sessionIdFocus,
                message: message,
            })
        );
    };
    const handleConnectToWebsocket = () => {
        connectToWebsocket({ appState, appActions, setLoading, sessionIds });
    };
    useEffect(() => {
        handleConnectToWebsocket();
    }, []);
    useEffect(() => {
        if (sessionMessageTextArea.current) {
            sessionMessageTextArea.current.focus();
        }
    }, [sessionIdFocus]);
    const SESSION_LISTL_PANEL_WIDTH = 451.65;
    if (_.isNil(appState.session.connection))
        return (
            <NonIdealState
                icon={faIcon({ icon: faSignalStreamSlash, size: 50 })}
                title={loading ? "Connecting" : "No connection"}
                action={
                    <Button
                        onClick={handleConnectToWebsocket}
                        intent={Intent.PRIMARY}
                        large
                        loading={loading}
                        text="Reconnect"
                    />
                }
            />
        );
    return (
        <>
            <div
                style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    height: "calc(100% - 1px)",
                    width: SESSION_LISTL_PANEL_WIDTH,
                }}
            >
                <div
                    style={{
                        padding: 20,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                    }}
                >
                    <ButtonGroup large>
                        <Button
                            disabled={_.isNil(appState.session.connection)}
                            text="New"
                            outlined
                            intent={Intent.PRIMARY}
                            onClick={() => {
                                if (_.isNil(appState.session.connection))
                                    return;
                                appActions.session.createSession({
                                    platform: appState.session.platform,
                                    connection: appState.session.connection,
                                });
                            }}
                            rightIcon={faIcon({ icon: faInboxOut })}
                        />
                        <Popover
                            placement="bottom"
                            content={
                                <div style={{ padding: 10 }}>
                                    <H5>Join an existing session</H5>
                                    <InputGroup
                                        large
                                        fill
                                        value={joinSessionId}
                                        onChange={(event) => {
                                            setJoinSessionId(
                                                event.target.value
                                            );
                                        }}
                                        rightElement={
                                            <Button
                                                className={
                                                    Classes.POPOVER_DISMISS
                                                }
                                                minimal
                                                text="Join"
                                                onClick={() => {
                                                    if (
                                                        _.isEmpty(
                                                            joinSessionId
                                                        ) ||
                                                        _.isNil(
                                                            appState.session
                                                                .connection
                                                        ) ||
                                                        _.includes(
                                                            sessionIds,
                                                            joinSessionId
                                                        )
                                                    )
                                                        return;
                                                    appActions.session.observeSession(
                                                        {
                                                            sessionId:
                                                                joinSessionId,
                                                            connection:
                                                                appState.session
                                                                    .connection,
                                                        }
                                                    );
                                                    setJoinSessionId("");
                                                }}
                                                intent={Intent.SUCCESS}
                                            />
                                        }
                                    />
                                </div>
                            }
                        >
                            <Button
                                outlined
                                icon={faIcon({ icon: faCaretDown })}
                            />
                        </Popover>
                    </ButtonGroup>
                </div>
                {_.isEmpty(appState.session.sessionIds) ? (
                    <Card
                        style={{
                            padding: 0,
                            marginTop: 1,
                            height: "calc(100% - 80px)",
                            width: "calc(100% - 1.35px)",
                            borderRadius: 0,
                        }}
                    >
                        <NonIdealState
                            icon={faIcon({ icon: faInboxIn, size: 50 })}
                            title="Sessions"
                        />
                    </Card>
                ) : (
                    <SessionList />
                )}
            </div>
            <div
                style={{
                    height: "calc(100% - 80px)",
                    marginLeft: SESSION_LISTL_PANEL_WIDTH,
                    width: `calc(100vw - ${
                        SESSION_LISTL_PANEL_WIDTH + 160.55
                    }px)`,
                }}
            >
                <Card
                    style={{
                        borderRadius: 0,
                        display: "flex",
                        alignItems: "center",
                        height: 80,
                        justifyContent: "space-between",
                    }}
                >
                    <H4
                        className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                        style={{ margin: 0 }}
                    >
                        {sessionIdFocus}
                    </H4>
                </Card>
                {_.isNull(sessionIdFocus) ? (
                    <NonIdealState
                        icon={faIcon({ icon: faMessages, size: 50 })}
                        title="Messages"
                    />
                ) : (
                    <>
                        <div style={{ height: "calc(100% - 131px" }}>
                            <SessionMessages />
                        </div>
                        <div
                            style={{
                                padding: 20,
                                position: "relative",
                                height: "calc(100% - 772px",
                                borderTop: "1px solid rgba(17, 20, 24, 0.15)",
                            }}
                        >
                            <div
                                style={{
                                    position: "absolute",
                                    height: "calc(100% - 40px)",
                                    top: "50%",
                                    transform: "translateY(-50%)",
                                    msTransform: "translateY(-50%)",
                                    left: 20,
                                }}
                            >
                                <Popover
                                    minimal
                                    placement="top-start"
                                    targetProps={{ style: { height: "100%" } }}
                                    content={
                                        <Menu large>
                                            <MenuItem
                                                disabled
                                                icon={faIcon({
                                                    icon: faSquareDashedCirclePlus,
                                                })}
                                                text="Add agent"
                                            ></MenuItem>
                                        </Menu>
                                    }
                                >
                                    <Button
                                        large
                                        minimal
                                        style={{
                                            borderTopRightRadius: 0,
                                            borderBottomRightRadius: 0,
                                            paddingBottom: 62,
                                            paddingTop: 12,
                                        }}
                                        icon={faIcon({ icon: faCirclePlus })}
                                    />
                                </Popover>
                            </div>
                            <TextArea
                                inputRef={sessionMessageTextArea}
                                style={{
                                    resize: "none",
                                    minHeight: "100%",
                                    paddingLeft: 50,
                                }}
                                value={message}
                                placeholder={`Message @${sessionIdFocus}`}
                                onChange={(event) => {
                                    setMessage(event.target.value);
                                }}
                                onKeyDown={(event) => {
                                    if (
                                        _.isEqual(event.key, "Enter") &&
                                        !event.shiftKey
                                    ) {
                                        sendSessionMessage(message);
                                        event.preventDefault();
                                    }
                                }}
                                fill
                            />
                        </div>
                    </>
                )}
            </div>
        </>
    );
}

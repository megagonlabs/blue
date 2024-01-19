import { AppContext } from "@/components/app-context";
import { faIcon } from "@/components/icon";
import SessionList from "@/components/sessions/SessionList";
import SessionMessages from "@/components/sessions/SessionMessages";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
    Card,
    Classes,
    H4,
    InputGroup,
    Intent,
    NonIdealState,
} from "@blueprintjs/core";
import {
    faArrowRightFromBracket,
    faArrowUpFromLine,
    faBarsFilter,
    faInboxIn,
    faInboxOut,
    faMessages,
    faSignalStreamSlash,
} from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
export default function Sessions() {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [message, setMessage] = useState("");
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
    const connectToWebsocket = () => {
        if (!_.isNil(appState.session.connection)) return;
        try {
            // Creating an instance of the WebSocket
            const socket = new WebSocket("ws://localhost:5050/sessions/ws");
            // Listening to messages from the server
            socket.onmessage = (event) => {
                try {
                    // parse the data from string to JSON object
                    const data = JSON.parse(event.data);
                    // If the data is of type SESSION_MESSAGE
                    if (_.isEqual(data["type"], "SESSION_MESSAGE")) {
                        appActions.session.addSessionMessage(data);
                    }
                } catch (e) {
                    AppToaster.show({
                        intent: Intent.PRIMARY,
                        message: event.data,
                    });
                    console.log(event.data);
                    console.error(e);
                }
            };
            socket.onerror = () => {
                appActions.session.setConnection(null);
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: `Failed to connect to websocketc (onerror)`,
                });
            };
            socket.onclose = () => {
                appActions.session.setConnection(null);
                AppToaster.show({
                    intent: Intent.PRIMARY,
                    message: "Connected closed",
                });
            };
            // Adding an event listener to when the connection is opened
            socket.onopen = () => {
                appActions.session.setConnection(socket);
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: "Connection established",
                });
            };
        } catch (e) {
            appActions.session.setConnection(null);
            AppToaster.show({
                intent: Intent.SUCCESS,
                message: `Failed to connect to websocket: ${e}`,
            });
        }
    };
    useEffect(() => {
        connectToWebsocket();
    }, []);
    const SESSION_LISTL_PANEL_WIDTH = 451.65;
    if (_.isNil(appState.session.connection))
        return (
            <NonIdealState
                icon={faIcon({ icon: faSignalStreamSlash, size: 50 })}
                title="No connection"
                action={
                    <Button
                        onClick={connectToWebsocket}
                        intent={Intent.PRIMARY}
                        outlined
                        large
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
                    <Button
                        text="Filter"
                        large
                        outlined
                        rightIcon={faIcon({ icon: faBarsFilter })}
                    />
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
                        justifyContent: "space-between",
                    }}
                >
                    <H4
                        className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                        style={{ margin: 0 }}
                    >
                        {sessionIdFocus}
                    </H4>
                    <Button
                        disabled={_.isNil(appState.session.sessionIdFocus)}
                        text="Leave"
                        intent={Intent.WARNING}
                        large
                        outlined
                        rightIcon={faIcon({ icon: faArrowRightFromBracket })}
                    />
                </Card>
                {_.isNull(sessionIdFocus) ? (
                    <NonIdealState
                        icon={faIcon({ icon: faMessages, size: 50 })}
                        title="Messages"
                    />
                ) : (
                    <>
                        <div
                            style={{
                                height: "calc(100% - 81px",
                            }}
                        >
                            <SessionMessages />
                        </div>
                        <div
                            style={{
                                padding: 20,
                                width: "100%",
                                display: "flex",
                                alignItems: "center",
                                borderTop: "1px solid rgba(17, 20, 24, 0.15)",
                            }}
                        >
                            <InputGroup
                                fill
                                large
                                value={message}
                                placeholder="Message"
                                onChange={(event) => {
                                    setMessage(event.target.value);
                                }}
                                onKeyDown={(event) => {
                                    if (_.isEqual(event.key, "Enter")) {
                                        sendSessionMessage(message);
                                    }
                                }}
                                rightElement={
                                    <Button
                                        minimal
                                        intent={Intent.PRIMARY}
                                        text="Send"
                                        onClick={() => {
                                            sendSessionMessage(message);
                                        }}
                                        rightIcon={faIcon({
                                            icon: faArrowUpFromLine,
                                        })}
                                    />
                                }
                            />
                        </div>
                    </>
                )}
            </div>
        </>
    );
}

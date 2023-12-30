import { AppContext } from "@/components/app-context";
import { faIcon } from "@/components/icon";
import SessionList from "@/components/sessions/SessionList";
import SessionMessages from "@/components/sessions/SessionMessages";
import { AppToaster } from "@/components/toaster";
import { Card, Intent, NonIdealState } from "@blueprintjs/core";
import { faInboxIn, faMessages } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useContext, useEffect } from "react";
export default function Sessions() {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    useEffect(() => {
        try {
            // Creating an instance of the WebSocket
            const socket = new WebSocket("ws://localhost:5000/sessions/ws");
            // Adding an event listener to when the connection is opened
            socket.onopen = () => {
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: "Connection established",
                });
            };
            // Listening to messages from the server
            socket.onmessage = (event) => {
                try {
                    // parse the data from string to JSON object
                    const data = JSON.parse(event.data);
                    // If the message is of type connect
                    if (_.isEqual(data["type"], "message")) {
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
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: `Failed to connect to websocketc (onerror)`,
                });
            };
            socket.close = () => {
                AppToaster.show({
                    intent: Intent.PRIMARY,
                    message: "Connected closed",
                });
            };
        } catch (e) {
            AppToaster.show({
                intent: Intent.SUCCESS,
                message: `Failed to connect to websocket: ${e}`,
            });
        }
    }, []);
    const SESSION_LISTL_PANEL_WIDTH = 451.65;
    return (
        <>
            <div
                style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    height: "100%",
                    width: SESSION_LISTL_PANEL_WIDTH,
                }}
            >
                {_.isEmpty(appState.session.sessionIds) ? (
                    <Card
                        style={{ padding: 0, height: "100%", borderRadius: 0 }}
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
                    height: "100%",
                    marginLeft: SESSION_LISTL_PANEL_WIDTH,
                    width: `calc(100vw - ${
                        SESSION_LISTL_PANEL_WIDTH + 150.55
                    }px)`,
                }}
            >
                {_.isNull(sessionIdFocus) ? (
                    <NonIdealState
                        icon={faIcon({ icon: faMessages, size: 50 })}
                        title="Messages"
                    />
                ) : (
                    <SessionMessages />
                )}
            </div>
        </>
    );
}

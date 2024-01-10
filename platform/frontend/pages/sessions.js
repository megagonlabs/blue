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
    Intent,
    NonIdealState,
    Popover,
} from "@blueprintjs/core";
import {
    faArrowRightFromArc,
    faBarsFilter,
    faCaretDown,
    faInboxIn,
    faInboxOut,
    faMessages,
} from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useContext, useEffect } from "react";
export default function Sessions() {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    useEffect(() => {
        try {
            // Creating an instance of the WebSocket
            const socket = new WebSocket("ws://localhost:5050/sessions/ws");
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
                            text="New session"
                            outlined
                            intent={Intent.PRIMARY}
                            rightIcon={faIcon({ icon: faInboxOut })}
                        />
                        <Popover
                            minimal
                            placement="bottom-end"
                            content={<div>Join existing session</div>}
                        >
                            <Button
                                outlined
                                rightIcon={faIcon({ icon: faCaretDown })}
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
                        text="Leave session"
                        intent={Intent.WARNING}
                        large
                        outlined
                        rightIcon={faIcon({ icon: faArrowRightFromArc })}
                    />
                </Card>
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

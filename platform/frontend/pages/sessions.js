import { actionToaster, createToast } from "@/components/toaster";
import { Intent } from "@blueprintjs/core";
import _ from "lodash";
import { useEffect } from "react";
export default function Sessions() {
    useEffect(() => {
        try {
            // Creating an instance of the WebSocket
            const socket = new WebSocket("ws://localhost:5000/sessions");
            // Adding an event listener to when the connection is opened
            socket.onopen = (ws, event) =>
                actionToaster.show(
                    createToast({
                        intent: Intent.SUCCESS,
                        message: "Connection established",
                    })
                );
            // Listening to messages from the server
            socket.onmessage = (event) => {
                try {
                    // parse the data from string to JSON object
                    const data = JSON.parse(event.data);
                    // If the message is of type connect
                    // set the client id
                    if (_.isEqual(data["type"], "connect")) {
                        actionToaster.show(
                            createToast({
                                intent: Intent.PRIMARY,
                                message: JSON.stringify(data),
                            })
                        );
                    } else if (_.isEqual(data["type"], "disconnected")) {
                        // if another client get disconnected show the current client
                        // that the other user left
                        actionToaster.show(
                            createToast({
                                intent: Intent.PRIMARY,
                                message: `Client ${data["id"]} disconnected`,
                            })
                        );
                    } else {
                        // if it is a regular message add it to the array of messages.
                        actionToaster.show(
                            createToast({
                                intent: Intent.PRIMARY,
                                message: JSON.stringify(data),
                            })
                        );
                    }
                } catch (e) {
                    console.log(event.data);
                    console.error(e);
                }
            };
            socket.onerror = (event) =>
                actionToaster.show(
                    createToast({
                        intent: Intent.DANGER,
                        message: `Failed to connect to websocket`,
                    })
                );
            socket.close = (event) =>
                actionToaster.show(
                    createToast({
                        intent: Intent.PRIMARY,
                        message: "Connected closed",
                    })
                );
        } catch (e) {
            actionToaster.show(
                createToast({
                    intent: Intent.SUCCESS,
                    message: `Failed to connect to websocket: ${e}`,
                })
            );
        }
    }, []);
    return <div></div>;
}

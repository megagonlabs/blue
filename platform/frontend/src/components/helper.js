const { faPenSwirl } = require("@fortawesome/pro-duotone-svg-icons");
const { faIcon } = require("./icon");
const { ProgressBar, Classes, Intent } = require("@blueprintjs/core");
const classNames = require("classnames");
const _ = require("lodash");
const { AppToaster } = require("./toaster");
const renderProgress = (progress, requestError = false) => {
    return {
        icon: faIcon({ icon: faPenSwirl }),
        message: (
            <ProgressBar
                className={classNames("margin-top-5", {
                    [Classes.PROGRESS_NO_STRIPES]: progress >= 100,
                })}
                intent={
                    requestError
                        ? Intent.DANGER
                        : progress < 100
                        ? Intent.PRIMARY
                        : Intent.SUCCESS
                }
                value={progress / 100}
            />
        ),
        timeout: progress < 100 ? 0 : 2000,
    };
};
module.exports = {
    constructSavePropertyRequests: ({
        axios,
        difference,
        appState,
        entity,
        editEntity,
    }) => {
        let tasks = [];
        if (_.isArray(difference)) {
            for (var i = 0; i < difference.length; i++) {
                const kind = difference[i].kind,
                    path = difference[i].path[0];
                if (_.isEqual(kind, "D")) {
                    tasks.push(
                        new Promise((resolve, reject) => {
                            axios
                                .delete(
                                    `/agents/${appState.agent.registryName}/agent/${entity.name}/property/${path}`
                                )
                                .then(() => {
                                    resolve(true);
                                })
                                .catch((error) => {
                                    AppToaster.show({
                                        intent: Intent.DANGER,
                                        message: `${error.name}: ${error.message}`,
                                    });
                                    reject(false);
                                });
                        })
                    );
                } else {
                    tasks.push(
                        new Promise((resolve, reject) => {
                            axios
                                .post(
                                    `/agents/${appState.agent.registryName}/agent/${entity.name}/property/${path}`,
                                    editEntity.properties[path],
                                    {
                                        headers: {
                                            "Content-type": "application/json",
                                        },
                                    }
                                )
                                .then(() => {
                                    resolve(true);
                                })
                                .catch((error) => {
                                    AppToaster.show({
                                        intent: Intent.DANGER,
                                        message: `${error.name}: ${error.message}`,
                                    });
                                    reject(false);
                                });
                        })
                    );
                }
            }
        }
        return tasks;
    },
    settlePromises: (tasks, callback) => {
        (async () => {
            let progress = 0,
                requestError = false;
            const key = AppToaster.show(renderProgress(progress));
            const promises = tasks.map((task) => {
                return task
                    .catch((status) => {
                        if (!status) {
                            requestError = true;
                        }
                    })
                    .finally(() => {
                        progress += 100 / tasks.length;
                        AppToaster.show(
                            renderProgress(progress, requestError),
                            key
                        );
                    });
            });
            await Promise.allSettled(promises);
            callback(requestError);
        })();
    },
    connectToWebsocket: ({ appState, appActions, setLoading, sessionIds }) => {
        if (!_.isNil(appState.session.connection)) return;
        if (_.isFunction(setLoading)) {
            setLoading(true);
        }
        try {
            console.log(process.env.NEXT_PUBLIC_API_SERVER);
            // Creating an instance of the WebSocket
            const socket = new WebSocket(
                `${process.env.NEXT_PUBLIC_WS_SERVER}/sessions/ws`
            );
            // Listening to messages from the server
            socket.onmessage = (event) => {
                try {
                    // parse the data from string to JSON object
                    const data = JSON.parse(event.data);
                    // If the data is of type SESSION_MESSAGE
                    if (_.isEqual(data["type"], "SESSION_MESSAGE")) {
                        appActions.session.addSessionMessage(data);
                    } else if (_.isEqual(data["type"], "CONNECTED")) {
                        appActions.session.setState({
                            key: "connectionId",
                            value: data.id,
                        });
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
                if (_.isFunction(setLoading)) {
                    setLoading(false);
                }
                appActions.session.setState({ key: "connection", value: null });
                AppToaster.show({
                    intent: Intent.DANGER,
                    message: `Failed to connect to websocketc (onerror)`,
                });
            };
            socket.onclose = () => {
                if (_.isFunction(setLoading)) {
                    setLoading(false);
                }
                appActions.session.setState({ key: "connection", value: null });
                AppToaster.show({
                    intent: Intent.PRIMARY,
                    message: "Connected closed",
                });
            };
            // Adding an event listener to when the connection is opened
            socket.onopen = () => {
                if (_.isFunction(setLoading)) {
                    setLoading(false);
                }
                appActions.session.setState({
                    key: "connection",
                    value: socket,
                });
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: "Connection established",
                    timeout: 2000,
                });
                if (!_.isEmpty(sessionIds)) {
                    for (var i = 0; i < sessionIds.length; i++) {
                        appActions.session.observeSession({
                            sessionId: sessionIds[i],
                            connection: socket,
                        });
                    }
                }
            };
        } catch (e) {
            if (_.isFunction(setLoading)) {
                setLoading(false);
            }
            appActions.session.setState({ key: "connection", value: null });
            AppToaster.show({
                intent: Intent.SUCCESS,
                message: `Failed to connect to websocket: ${e}`,
            });
        }
    },
};

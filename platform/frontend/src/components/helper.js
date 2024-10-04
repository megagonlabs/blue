const { faPenSwirl } = require("@fortawesome/sharp-duotone-solid-svg-icons");
const { faIcon } = require("@/components/icon");
const { ProgressBar, Classes, Intent } = require("@blueprintjs/core");
const classNames = require("classnames");
const _ = require("lodash");
const { AppToaster, ProgressToaster } = require("@/components/toaster");
const { default: transform } = require("css-to-react-native");
const renderProgress = (progress, requestError = false) => {
    return {
        icon: faIcon({ icon: faPenSwirl }),
        isCloseButtonShown: false,
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
    };
};
const waitForOpenConnection = (socket) => {
    return new Promise((resolve, reject) => {
        const maxNumberOfAttempts = 10;
        const intervalTime = 200; //ms
        let currentAttempt = 0;
        const interval = setInterval(() => {
            if (currentAttempt > maxNumberOfAttempts - 1) {
                clearInterval(interval);
                reject(new Error("Maximum number of attempts exceeded"));
            } else if (_.isEqual(socket.readyState, WebSocket.OPEN)) {
                clearInterval(interval);
                resolve();
            }
            currentAttempt++;
        }, intervalTime);
    });
};
const sendSocketMessage = async (socket, message, retries = 0) => {
    try {
        socket.send(message);
    } catch (error) {
        if (retries < 4 && _.isEqual(error.name, "InvalidStateError")) {
            await waitForOpenConnection(socket);
            sendSocketMessage(socket, message, retries + 1);
        } else {
            console.error(error);
        }
    }
};
module.exports = {
    Queue: class Queue {
        constructor() {
            this.items = {};
            this.front = 0;
            this.back = 0;
        }
        enqueue(item) {
            this.items[this.back] = item;
            this.back++;
        }
        isEmpty() {
            return _.isEmpty(this.items);
        }
        dequeue() {
            const item = this.items[this.front];
            delete this.items[this.front];
            this.front++;
            return item;
        }
        peek() {
            return this.items[this.front];
        }
    },
    constructSavePropertyRequests: ({ axios, url, difference, editEntity }) => {
        let tasks = [];
        if (_.isArray(difference)) {
            for (var i = 0; i < difference.length; i++) {
                const kind = difference[i].kind,
                    path = difference[i].path[0];
                if (_.isEqual(kind, "D")) {
                    tasks.push(
                        new Promise((resolve, reject) => {
                            axios
                                .delete(url + "/" + path)
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
                                    url + "/" + path,
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
            const key = ProgressToaster.show(
                renderProgress(_.isEmpty(tasks) ? 100 : progress)
            );
            const promises = tasks.map((task) => {
                return task
                    .catch((status) => {
                        if (!status) {
                            requestError = true;
                        }
                    })
                    .finally(() => {
                        progress += 100 / tasks.length;
                        ProgressToaster.show(
                            renderProgress(progress, requestError),
                            key
                        );
                    });
            });
            await Promise.allSettled(promises);
            callback(requestError);
        })();
    },
    hasIntersection: (array1, array2) => {
        return _.some(array1, _.ary(_.partial(_.includes, array2), 1));
    },
    hasTrue: (array) => {
        return _.some(array, Boolean);
    },
    convertCss: (style) => {
        try {
            return transform(Object.entries(style));
        } catch (error) {
            return style;
        }
    },
    sendSocketMessage,
};

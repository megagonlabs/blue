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
    shallowDiff: (base, compared) => {
        let updated = [],
            deleted = [],
            added = [];
        const comparedKeys = Object.keys(compared);
        for (let i = 0; i < _.size(comparedKeys); i++) {
            const key = comparedKeys[i];
            // check for updated
            if (_.has(base, key)) {
                if (!_.isEqual(base[key], compared[key])) updated.push(key);
            } else {
                added.push(key);
            }
        }
        const baseKeys = Object.keys(base);
        for (let i = 0; i < _.size(baseKeys); i++) {
            const key = baseKeys[i];
            // check for deleted
            if (!_.has(compared, key)) {
                deleted.push(key);
            }
        }
        return { updated, deleted, added };
    },
    constructSavePropertyRequests: ({ axios, url, difference, properties }) => {
        let tasks = [];
        const { updated, deleted, added } = difference;
        if (!_.isEmpty(deleted)) {
            for (let i = 0; i < _.size(deleted); i++) {
                tasks.push(
                    new Promise((resolve, reject) => {
                        axios
                            .delete(`${url}/${deleted[i]}`)
                            .then(() => resolve(true))
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
        const posts = [...updated, ...added];
        if (!_.isEmpty(posts)) {
            for (let i = 0; i < _.size(posts); i++) {
                const key = posts[i];
                tasks.push(
                    new Promise((resolve, reject) => {
                        axios
                            .post(
                                `${url}/${key}`,
                                _.get(properties, key, null),
                                {
                                    headers: {
                                        "Content-type": "application/json",
                                    },
                                }
                            )
                            .then(() => resolve(true))
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

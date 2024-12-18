const {
    faPenSwirl,
    faCopy,
    faExclamation,
} = require("@fortawesome/sharp-duotone-solid-svg-icons");
const { faIcon } = require("@/components/icon");
const { ProgressBar, Classes, Intent, Button } = require("@blueprintjs/core");
const classNames = require("classnames");
const _ = require("lodash");
const { AppToaster, ProgressToaster } = require("@/components/toaster");
const { default: transform } = require("css-to-react-native");
const copy = require("copy-to-clipboard");
const renderProgress = (progress = 0, requestError = false) => {
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
const axiosErrorToast = (error) => {
    let message = "";
    try {
        message = `${error.name}: ${error.message}`;
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        if (error.response)
            message = `[${error.response.status}]: ${_.get(
                error,
                "response.data.message",
                "-"
            )}`;
    } catch (error) {
        message = "Request Error";
    }
    AppToaster.show({
        icon: faIcon({ icon: faExclamation }),
        intent: Intent.DANGER,
        message: <div className="multiline-ellipsis-5">{message}</div>,
        action: {
            icon: faIcon({ icon: faCopy }),
            onClick: () => copy(message),
            text: "Copy",
        },
    });
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
    mergeTrackerData: (oldData = [], newData = []) => {
        const combinedData = oldData.concat(newData);
        return _.takeRight(
            _.sortBy(_.uniqBy(combinedData, "epoch"), "epoch"),
            60
        );
    },
    populateRouterPathname: (router) => {
        let pathname = router.pathname;
        const params = Object.keys(router.query);
        for (let i = 0; i < _.size(params); i++) {
            pathname = pathname.replace(
                `[${params[i]}]`,
                router.query[params[i]]
            );
        }
        return pathname;
    },
    shallowDiff: (base, compared) => {
        let updated = [],
            deleted = [],
            added = [];
        const comparedKeys = _.keys(compared);
        for (let i = 0; i < _.size(comparedKeys); i++) {
            const key = comparedKeys[i];
            // check for updated
            if (_.has(base, key)) {
                if (!_.isEqual(base[key], compared[key])) updated.push(key);
            } else {
                added.push(key);
            }
        }
        const baseKeys = _.keys(base);
        for (let i = 0; i < _.size(baseKeys); i++) {
            const key = baseKeys[i];
            // check for deleted
            if (!_.has(compared, key)) {
                deleted.push(key);
            }
        }
        return { updated, deleted, added };
    },
    safeJsonParse: (json) => {
        try {
            if (_.isNil(json)) return {};
            return JSON.parse(json);
        } catch (error) {
            return {};
        }
    },
    axiosErrorToast,
    constructSavePropertyRequests: ({ axios, url, difference, properties }) => {
        let tasks = [];
        const { updated, deleted, added } = difference;
        if (!_.isEmpty(deleted)) {
            for (let i = 0; i < _.size(deleted); i++) {
                tasks.push(
                    new Promise((resolve, reject) =>
                        axios
                            .delete(`${url}/${deleted[i]}`)
                            .then(() => resolve(true))
                            .catch((error) => axiosErrorToast(error))
                    )
                );
            }
        }
        const posts = [...updated, ...added];
        if (!_.isEmpty(posts)) {
            for (let i = 0; i < _.size(posts); i++) {
                const key = posts[i];
                tasks.push(
                    new Promise((resolve, reject) =>
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
                                axiosErrorToast(error);
                                reject(false);
                            })
                    )
                );
            }
        }
        return tasks;
    },
    settlePromises: (tasks, callback) => {
        (async () => {
            let requestError = false;
            const key = ProgressToaster.show(
                renderProgress(_.isEmpty(tasks) ? 100 : 0)
            );
            const promises = tasks.map((task, index) => {
                return task
                    .catch((status) => {
                        if (!status) requestError = true;
                    })
                    .finally(() => {
                        const progress = ((index + 1) / tasks.length) * 100;
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

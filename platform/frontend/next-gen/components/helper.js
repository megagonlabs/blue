const {
    faExclamation,
    faCopy,
    faPenSwirl,
} = require("@fortawesome/sharp-duotone-solid-svg-icons");
const { AppToaster, ProgressToaster } = require("./toaster");
const classNames = require("classnames");
const { FAIcon } = require("./FAIcon");
const { Intent, ProgressBar, Classes } = require("@blueprintjs/core");
const copy = require("copy-to-clipboard");
const { default: transform } = require("css-to-react-native");
const renderProgress = (progress = 0, requestError = false) => {
    return {
        icon: <FAIcon icon={faPenSwirl} />,
        isCloseButtonShown: false,
        message: (
            <ProgressBar
                style={{ marginTop: 5 }}
                className={classNames({
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
const showAxiosErrorToast = (error) => {
    let message = "";
    try {
        message = `${error.name}: ${error.message}`;
        // the request was made and the server responded with a status code
        // that falls out of the range of 2xx
        if (error.response)
            message = `[${error.response.status} ${
                error.response.statusText
            }]: ${_.get(error, "response.data.message", "-")}`;
    } catch (error) {
        message = "Request Error";
    }
    AppToaster.show({
        icon: <FAIcon icon={faExclamation} />,
        intent: Intent.DANGER,
        message: <div className="multiline-ellipsis-5">{message}</div>,
        action: {
            icon: <FAIcon icon={faCopy} />,
            onClick: () => {
                copy(message);
            },
            text: "Copy",
        },
    });
};
module.exports = {
    waitForOpenConnection: (socket) => {
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
    },
    hasIntersection: (left, right) => {
        return _.some(left, _.ary(_.partial(_.includes, right), 1));
    },
    getUpdatePropertyPromises: ({ axios, url, diffs, properties }) => {
        let tasks = [];
        const { updated, deleted, added } = diffs;
        for (let i = 0; i < _.size(deleted); i++) {
            tasks.push(
                new Promise((resolve, reject) => {
                    axios
                        .delete(`${url}/${deleted[i]}`)
                        .then(() => {
                            resolve(true);
                        })
                        .catch((error) => {
                            showAxiosErrorToast(error);
                            reject(false);
                        });
                })
            );
        }
        const posts = [...updated, ...added];
        for (let i = 0; i < _.size(posts); i++) {
            const key = posts[i];
            tasks.push(
                new Promise((resolve, reject) => {
                    axios
                        .post(`${url}/${key}`, {
                            [key]: _.get(properties, key, null),
                        })
                        .then(() => {
                            resolve(true);
                        })
                        .catch((error) => {
                            showAxiosErrorToast(error);
                            reject(false);
                        });
                })
            );
        }
        return tasks;
    },
    showAxiosErrorToast,
    convertCss: (style) => {
        try {
            return transform(_.entries(style));
        } catch (error) {
            return style;
        }
    },
    settlePromises: (tasks, callback) => {
        (async () => {
            let error = false;
            const key = ProgressToaster.show(
                renderProgress(_.isEmpty(tasks) ? 100 : 0)
            );
            let count = 0;
            const promises = tasks.map((task) => {
                return task
                    .catch((reason) => {
                        error = true;
                        return new Promise((resolve, reject) => reject(reason));
                    })
                    .finally(() => {
                        const progress = (++count / tasks.length) * 100;
                        ProgressToaster.show(
                            renderProgress(progress, error),
                            key
                        );
                    });
            });
            Promise.allSettled(promises).then((results) => {
                callback({ results, error });
            });
        })();
    },
};

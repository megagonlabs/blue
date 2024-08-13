const { faPenSwirl } = require("@fortawesome/pro-duotone-svg-icons");
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
        timeout: progress < 100 ? 0 : 2000,
    };
};
module.exports = {
    getAgentFromStream: (stream) => {
        let agent = {};
        try {
            const agentTypeId = stream
                .match(/(?<=:AGENT:\s*).*?(?=\s*:OUTPUT:)/gs)[0]
                .split(":");
            agent = {
                type: _.get(agentTypeId, 0, null),
                id: _.get(agentTypeId, 1, null),
            };
        } catch (error) {}
        return agent;
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
    hasInteraction: (array1, array2) => {
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
};

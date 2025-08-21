import { faPenSwirl } from "@fortawesome/sharp-duotone-solid-svg-icons";
import dagre from "dagre";
import _ from "lodash";
import EntityDisplayName from "./registries/EntityDisplayName";
import RegistryEntityIcon from "./registries/RegistryEntityIcon";
const classNames = require("classnames");
const { FAIcon } = require("./FAIcon");
const { Intent, ProgressBar, Classes } = require("@blueprintjs/core");
const { default: transform } = require("css-to-react-native");
const { ENTITY_MAIN_INFO_PROPERTY_KEYS } = require("./constants");
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
const constructAgentTree = (agent) => {
    const derivedAgents = _.values(_.get(agent, "contents.agent", {}));
    let node = {
        id: agent.name,
        icon: (
            <RegistryEntityIcon
                type={"agent"}
                maxSize={20}
                content={_.get(agent, "icon", null)}
            />
        ),
        agent,
        label: (
            <div
                className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                style={{ marginLeft: 7 }}
            >
                <EntityDisplayName entity={agent} />
            </div>
        ),
        childNodes: [],
        hasCaret: false,
    };
    for (let i = 0; i < _.size(derivedAgents); i++) {
        node.childNodes.push(constructAgentTree(derivedAgents[i]));
    }
    if (!_.isEmpty(node.childNodes)) {
        _.set(node, "hasCaret", true);
    }
    return node;
};
function base64ToWebsafe(base64) {
    return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
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
    scrollToTarget: (containerId, targetId) => {
        try {
            const scrollableContainer = document.getElementById(containerId);
            const targetElement = scrollableContainer.querySelector(
                `#${targetId}`
            );
            const scrollMargin = 20;
            if (scrollableContainer && targetElement) {
                const targetRect = targetElement.getBoundingClientRect();
                const scrollableRect =
                    scrollableContainer.getBoundingClientRect();
                const targetRelativeTop = targetRect.top - scrollableRect.top;
                let finalScrollPosition =
                    scrollableContainer.scrollTop +
                    targetRelativeTop -
                    scrollMargin;

                finalScrollPosition = Math.max(0, finalScrollPosition);
                setTimeout(() => {
                    scrollableContainer.scrollTop = finalScrollPosition;
                }, 0);
            }
        } catch (error) {}
    },
    canvasPreview: (image, canvas, crop, scale = 1, rotate = 0) => {
        const ctx = canvas.getContext("2d");
        if (!ctx) {
            throw new Error("No 2d context");
        }
        const scaleX = image.naturalWidth / image.width;
        const scaleY = image.naturalHeight / image.height;
        // devicePixelRatio slightly increases sharpness on retina devices
        // at the expense of slightly slower render times and needing to
        // size the image back down if you want to download/upload and be
        // true to the images natural size.
        const pixelRatio = window.devicePixelRatio;
        // const pixelRatio = 1
        canvas.width = Math.floor(crop.width * scaleX * pixelRatio);
        canvas.height = Math.floor(crop.height * scaleY * pixelRatio);
        ctx.scale(pixelRatio, pixelRatio);
        ctx.imageSmoothingQuality = "high";
        const cropX = crop.x * scaleX;
        const cropY = crop.y * scaleY;
        const rotateRads = rotate * (Math.PI / 180);
        const centerX = image.naturalWidth / 2;
        const centerY = image.naturalHeight / 2;
        ctx.save();
        // 5) Move the crop origin to the canvas origin (0,0)
        ctx.translate(-cropX, -cropY);
        // 4) Move the origin to the center of the original position
        ctx.translate(centerX, centerY);
        // 3) Rotate around the origin
        ctx.rotate(rotateRads);
        // 2) Scale the image
        ctx.scale(scale, scale);
        // 1) Move the center of the image to the origin (0,0)
        ctx.translate(-centerX, -centerY);
        ctx.drawImage(
            image,
            0,
            0,
            image.naturalWidth,
            image.naturalHeight,
            0,
            0,
            image.naturalWidth,
            image.naturalHeight
        );
        ctx.restore();
    },
    getReactFlowLayoutedElements: (nodes, edges, direction = "LR") => {
        const dagreGraph = new dagre.graphlib.Graph();
        dagreGraph.setDefaultEdgeLabel(() => ({}));
        dagreGraph.setGraph({
            rankdir: direction,
            compound: true,
            marginx: 20,
            marginy: 20,
        });
        for (let i = 0; i < _.size(nodes); i++) {
            const node = nodes[i];
            if (!node.width || !node.height) {
                dagreGraph.setNode(node.id, { width: 1, height: 1 });
            } else {
                dagreGraph.setNode(node.id, {
                    width: node.width,
                    height: node.height,
                });
            }
            if (node.parentId) {
                dagreGraph.setParent(node.id, node.parentId);
            }
        }
        for (let i = 0; i < _.size(edges); i++) {
            const edge = edges[i];
            dagreGraph.setEdge(edge.source, edge.target);
        }
        dagre.layout(dagreGraph);
        const newNodes = nodes.map((node) => {
            const graphNode = dagreGraph.node(node.id);
            const { width, height, x, y } = graphNode;
            const newNode = {
                ...node,
                position: {
                    x: x - width / 2,
                    y: y - height / 2,
                },
                width,
                height,
            };
            return newNode;
        });
        return { nodes: newNodes, edges };
    },
    insertBetween: (list, element) => {
        let array = _.cloneDeep(list);
        for (let i = 1; i < _.size(array); i += 2) {
            array.splice(i, 0, element);
        }
        return array;
    },
    encodeWebsafeBase64: (payload) => {
        return base64ToWebsafe(btoa(payload));
    },
    getEntityMainProperties: (properties) => {
        return _.cloneDeep(_.pick(properties, ENTITY_MAIN_INFO_PROPERTY_KEYS));
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
    getUpdatePropertyPromises: ({
        axios,
        url,
        diffs,
        properties,
        showAxiosErrorToast,
    }) => {
        let promises = [];
        const { updated, deleted, added } = diffs;
        for (let i = 0; i < _.size(deleted); i++) {
            promises.push(
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
            promises.push(
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
        return promises;
    },
    constructAgentTree,
    convertCss: (style) => {
        try {
            return transform(_.entries(style));
        } catch (error) {
            return style;
        }
    },
    settlePromises: (promises, callback, progressToaster) => {
        (async () => {
            let error = false;
            const key = progressToaster.show(
                renderProgress(_.isEmpty(promises) ? 100 : 0)
            );
            let count = 0;
            const mappedPromises = promises.map((promise) => {
                return promise
                    .catch((reason) => {
                        error = true;
                        return new Promise((resolve, reject) => reject(reason));
                    })
                    .finally(() => {
                        const progress = (++count / _.size(promises)) * 100;
                        progressToaster.show(
                            renderProgress(progress, error),
                            key
                        );
                    });
            });
            Promise.allSettled(mappedPromises).then((results) => {
                callback({ results, error });
            });
        })();
    },
};

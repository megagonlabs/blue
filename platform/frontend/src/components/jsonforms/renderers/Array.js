import { AppContext } from "@/components/contexts/app-context";
import { Queue, sendSocketMessage } from "@/components/helper";
import { useSocket } from "@/components/hooks/useSocket";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
    Classes,
    H6,
    Intent,
    Popover,
    Section,
    SectionCard,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowDown,
    faArrowUp,
    faDiagramNext,
    faPlus,
    faTrash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import {
    composePaths,
    createDefaultValue,
    findUISchema,
    isObjectArrayWithNesting,
    rankWith,
} from "@jsonforms/core";
import {
    JsonFormsDispatch,
    withArrayTranslationProps,
    withJsonFormsArrayControlProps,
    withTranslateProps,
} from "@jsonforms/react";
import _ from "lodash";
import { useContext, useEffect, useMemo } from "react";
import { v4 as uuidv4 } from "uuid";
const ArrayRenderer = ({
    label,
    data,
    translations,
    schema,
    rootSchema,
    uischema,
    uischemas,
    path,
    renderers,
    addItem,
    removeItems,
    moveUp,
    moveDown,
}) => {
    const { socket } = useSocket();
    const { appState, appActions } = useContext(AppContext);
    const childUiSchema = useMemo(
        () =>
            findUISchema(
                uischemas,
                schema,
                uischema.scope,
                path,
                undefined,
                uischema,
                rootSchema
            ),
        [uischemas, schema, path, uischema, rootSchema]
    );
    const visualization = _.get(uischema, "props.visualization", null);
    useEffect(() => {
        setTimeout(() => {
            sendSocketMessage(
                socket,
                JSON.stringify({
                    type: "INTERACTIVE_EVENT_MESSAGE",
                    stream_id: _.get(uischema, "props.streamId", null),
                    path: path,
                    form_id: _.get(uischema, "props.formId", null),
                    value: data,
                    timestamp: performance.timeOrigin + performance.now(),
                })
            );
        }, 0);
    }, [data]); // eslint-disable-line react-hooks/exhaustive-deps
    const setVisualization = () => {
        try {
            let visualValue = null;
            if (_.isEqual(visualization, "DAG")) {
                let fromTo = {},
                    toFrom = {},
                    uniqueNodes = new Set(),
                    nodeIds = {},
                    transitionNodes = [],
                    edgeType = "smoothstep";
                let edges = [];
                for (let i = 0; i < _.size(data); i++) {
                    const fromNode = data[i].from_agent,
                        toNode = data[i].to_agent;
                    if (!_.has(appState, ["agent", "icon", fromNode])) {
                        appActions.agent.fetchAttributes(fromNode);
                    }
                    if (!_.has(appState, ["agent", "icon", toNode])) {
                        appActions.agent.fetchAttributes(toNode);
                    }
                    uniqueNodes.add(fromNode);
                    uniqueNodes.add(toNode);
                    if (!_.has(nodeIds, fromNode)) {
                        nodeIds[fromNode] = uuidv4();
                    }
                    if (!_.has(nodeIds, toNode)) {
                        nodeIds[toNode] = uuidv4();
                    }
                    const transitionNodeId = uuidv4();
                    transitionNodes.push({
                        id: transitionNodeId,
                        data: {
                            fromParam: data[i].from_agent_param,
                            toParam: data[i].to_agent_param,
                        },
                        type: "transition-edge-node",
                    });
                    edges.push({
                        id: uuidv4(),
                        source: nodeIds[fromNode],
                        target: transitionNodeId,
                        animated: true,
                        type: edgeType,
                        style: { strokeWidth: 2 },
                    });
                    edges.push({
                        id: uuidv4(),
                        source: transitionNodeId,
                        target: nodeIds[toNode],
                        animated: true,
                        type: edgeType,
                        style: { strokeWidth: 2 },
                    });
                    if (_.has(fromTo, fromNode)) {
                        fromTo[fromNode].push(toNode);
                    } else {
                        fromTo[fromNode] = [toNode];
                    }
                    if (_.has(toFrom, toNode)) {
                        toFrom[toNode].push(fromNode);
                    } else {
                        toFrom[toNode] = [fromNode];
                    }
                }
                const getEndNodes = (dag) => {
                    let endNodes = new Set(),
                        visited = new Set(),
                        next = new Queue();
                    const nodes = _.keys(dag);
                    for (let i = 0; i < _.size(nodes); i++) {
                        next.enqueue(nodes[i]);
                    }
                    while (!next.isEmpty()) {
                        const current = next.dequeue();
                        if (visited.has(current)) {
                            continue;
                        }
                        const connected = _.get(dag, current, []);
                        if (_.isEmpty(connected)) {
                            // nothing connected to the node
                            endNodes.add(current);
                        } else {
                            for (let i = 0; i < _.size(connected); i++) {
                                next.enqueue(connected[i]);
                            }
                        }
                        visited.add(current);
                    }
                    return endNodes;
                };
                let inputNodes = getEndNodes(toFrom),
                    outputNodes = getEndNodes(fromTo);
                let nodes = _.toArray(uniqueNodes).map((node) => {
                    let nodeProps = {
                        id: nodeIds[node],
                        data: { label: node },
                        type: "agent-node",
                    };
                    if (inputNodes.has(node)) {
                        _.set(nodeProps, "data.input", true);
                    } else if (outputNodes.has(node)) {
                        _.set(nodeProps, "data.output", true);
                    } else {
                        _.set(nodeProps, "data.input", true);
                        _.set(nodeProps, "data.output", true);
                    }
                    return nodeProps;
                });
                nodes = nodes.concat(transitionNodes);
                visualValue = { nodes, edges };
            }
            appActions.session.setState({
                key: "visualization",
                value: visualValue,
            });
        } catch (error) {
            AppToaster.show({
                intent: Intent.DANGER,
                message: `Failed to initialize visualization: ${error}`,
            });
        }
    };
    return (
        <div>
            <H6 style={{ marginTop: 0, marginBottom: 15 }}>{label}</H6>
            {!_.isEmpty(data) ? (
                _.range(0, data.length).map((index) => {
                    const childPath = composePaths(path, String(index));
                    const content = (
                        <JsonFormsDispatch
                            schema={schema}
                            uischema={childUiSchema || uischema}
                            path={childPath}
                            key={childPath}
                            renderers={renderers}
                        />
                    );
                    return (
                        <Section
                            key={index}
                            style={{
                                marginBottom: 15,
                            }}
                            compact
                            title={<div>{index + 1}</div>}
                            rightElement={
                                <div>
                                    {index > 0 ? (
                                        <Tooltip
                                            minimal
                                            placement="bottom"
                                            content="Move up"
                                        >
                                            <Button
                                                onClick={() => {
                                                    moveUp(path, index)();
                                                }}
                                                minimal
                                                icon={faIcon({
                                                    icon: faArrowUp,
                                                })}
                                            />
                                        </Tooltip>
                                    ) : null}
                                    {index < _.size(data) - 1 ? (
                                        <Tooltip
                                            minimal
                                            placement="bottom"
                                            content="Move down"
                                        >
                                            <Button
                                                onClick={() => {
                                                    moveDown(path, index)();
                                                }}
                                                minimal
                                                icon={faIcon({
                                                    icon: faArrowDown,
                                                })}
                                            />
                                        </Tooltip>
                                    ) : null}
                                    <Popover
                                        content={
                                            <div style={{ padding: 15 }}>
                                                <Button
                                                    intent={Intent.DANGER}
                                                    className={
                                                        Classes.POPOVER_DISMISS
                                                    }
                                                    text="Confirm"
                                                    onClick={() =>
                                                        removeItems(path, [
                                                            index,
                                                        ])()
                                                    }
                                                />
                                            </div>
                                        }
                                        placement="bottom-end"
                                    >
                                        <Tooltip
                                            minimal
                                            placement="bottom-end"
                                            content={translations.removeTooltip}
                                        >
                                            <Button
                                                minimal
                                                intent={Intent.DANGER}
                                                icon={faIcon({ icon: faTrash })}
                                            />
                                        </Tooltip>
                                    </Popover>
                                </div>
                            }
                        >
                            <SectionCard>{content}</SectionCard>
                        </Section>
                    );
                })
            ) : (
                <div style={{ marginBottom: 15 }}>
                    {translations.noDataMessage}
                </div>
            )}
            <ButtonGroup
                fill
                style={{
                    maxWidth: _.includes(["DAG"], visualization)
                        ? 171.88
                        : 70.77,
                    marginBottom: 15,
                }}
            >
                <Tooltip
                    placement="top-start"
                    minimal
                    content={translations.addTooltip}
                >
                    <Button
                        icon={faIcon({ icon: faPlus })}
                        text="Add"
                        ellipsizeText
                        outlined
                        onClick={addItem(
                            path,
                            createDefaultValue(schema, rootSchema)
                        )}
                    />
                </Tooltip>
                {_.includes(["DAG"], visualization) ? (
                    <Button
                        ellipsizeText
                        disabled={_.isEmpty(data)}
                        outlined
                        text="Visualize"
                        onClick={setVisualization}
                        icon={faIcon({ icon: faDiagramNext })}
                    />
                ) : null}
            </ButtonGroup>
        </div>
    );
};
export default withJsonFormsArrayControlProps(
    withTranslateProps(withArrayTranslationProps(ArrayRenderer))
);
export const ArrayTester = rankWith(5, isObjectArrayWithNesting);

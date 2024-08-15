import { AppContext } from "@/components/contexts/app-context";
import { useSocket } from "@/components/hooks/useSocket";
import { faIcon } from "@/components/icon";
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
    faCircleNodes,
    faPlus,
    faTrash,
} from "@fortawesome/pro-duotone-svg-icons";
import {
    composePaths,
    createDefaultValue,
    findUISchema,
    isObjectArrayWithNesting,
    rankWith,
} from "@jsonforms/core";
import {
    JsonFormsDispatch,
    withJsonFormsArrayControlProps,
} from "@jsonforms/react";
import _ from "lodash";
import { useContext, useEffect, useMemo } from "react";
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
    const { appActions } = useContext(AppContext);
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
        [uischemas, schema, uischema.scope, path, uischema, rootSchema]
    );
    useEffect(() => {
        setTimeout(() => {
            socket.send(
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
    }, [data]);
    const setVisualization = () => {
        const position = { x: 0, y: 0 };
        const edgeType = "smoothstep";
        let nodes = [
            {
                id: "1",
                data: { label: "input" },
                position,
            },
            {
                id: "2",
                data: { label: "node 2" },
                position,
            },
            {
                id: "2a",
                data: { label: "node 2a" },
                position,
            },
            {
                id: "2b",
                data: { label: "node 2b" },
                position,
            },
            {
                id: "2c",
                data: { label: "node 2c" },
                position,
            },
            {
                id: "2d",
                data: { label: "node 2d" },
                position,
            },
            {
                id: "3",
                data: { label: "node 3" },
                position,
            },
            {
                id: "4",
                data: { label: "node 4" },
                position,
            },
            {
                id: "5",
                data: { label: "node 5" },
                position,
            },
            {
                id: "6",
                data: { label: "output" },
                position,
            },
            { id: "7", type: "output", data: { label: "output" }, position },
        ];
        let edges = [
            {
                id: "e12",
                source: "1",
                target: "2",
                type: edgeType,
                animated: true,
            },
            {
                id: "e13",
                source: "1",
                target: "3",
                type: edgeType,
                animated: true,
            },
            {
                id: "e22a",
                source: "2",
                target: "2a",
                type: edgeType,
                animated: true,
            },
            {
                id: "e22b",
                source: "2",
                target: "2b",
                type: edgeType,
                animated: true,
            },
            {
                id: "e22c",
                source: "2",
                target: "2c",
                type: edgeType,
                animated: true,
            },
            {
                id: "e2c2d",
                source: "2c",
                target: "2d",
                type: edgeType,
                animated: true,
            },
            {
                id: "e45",
                source: "4",
                target: "5",
                type: edgeType,
                animated: true,
            },
            {
                id: "e56",
                source: "5",
                target: "6",
                type: edgeType,
                animated: true,
            },
            {
                id: "e57",
                source: "5",
                target: "7",
                type: edgeType,
                animated: true,
            },
        ];
        appActions.session.setState({
            key: "visualization",
            value: { nodes, edges },
        });
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
                                            <div
                                                style={{
                                                    padding: 15,
                                                }}
                                            >
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
                                                icon={faIcon({
                                                    icon: faTrash,
                                                })}
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
            <ButtonGroup>
                <Tooltip
                    placement="top-start"
                    minimal
                    content={translations.addTooltip}
                >
                    <Button
                        icon={faIcon({ icon: faPlus })}
                        text="Add"
                        outlined
                        onClick={addItem(
                            path,
                            createDefaultValue(schema, rootSchema)
                        )}
                    />
                </Tooltip>
                <Button
                    outlined
                    text="Visualize"
                    onClick={setVisualization}
                    icon={faIcon({ icon: faCircleNodes })}
                />
            </ButtonGroup>
        </div>
    );
};
export default withJsonFormsArrayControlProps(ArrayRenderer);
export const ArrayTester = rankWith(5, isObjectArrayWithNesting);

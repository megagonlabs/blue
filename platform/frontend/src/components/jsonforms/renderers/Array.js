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
import _, { range } from "lodash";
import { useEffect, useMemo } from "react";
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
    return (
        <div>
            <H6 style={{ marginTop: 0, marginBottom: 15 }}>{label}</H6>
            {!_.isEmpty(data) ? (
                range(0, data.length).map((index) => {
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
                    disabled
                    outlined
                    text="Visualize"
                    icon={faIcon({ icon: faCircleNodes })}
                />
            </ButtonGroup>
        </div>
    );
};
export default withJsonFormsArrayControlProps(ArrayRenderer);
export const ArrayTester = rankWith(5, isObjectArrayWithNesting);

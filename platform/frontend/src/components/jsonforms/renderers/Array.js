import { StrictModeDroppable } from "@/components/dnd/StrictModeDroppable";
import { faIcon } from "@/components/icon";
import {
    Button,
    Classes,
    H6,
    Intent,
    Popover,
    Section,
    SectionCard,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowUpArrowDown,
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
import { useMemo } from "react";
import { DragDropContext, Draggable } from "react-beautiful-dnd";
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
    console.log(translations);
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
    const onDragEnd = (result) => {
        // dropped outside the list
        if (!result.destination) {
            return;
        }
        let from = result.source.index;
        let to = result.destination.index;
        while (from > to) {
            moveUp(path, from)();
            from -= 1;
        }
        while (from < to) {
            moveDown(path, from)();
            from += 1;
        }
    };
    return (
        <div>
            <H6 style={{ marginTop: 0, marginBottom: 15 }}>{label}</H6>
            {!_.isEmpty(data) ? (
                <DragDropContext onDragEnd={onDragEnd}>
                    <StrictModeDroppable droppableId={path}>
                        {(provided) => (
                            <div
                                {...provided.droppableProps}
                                ref={provided.innerRef}
                            >
                                {range(0, data.length).map((index) => {
                                    const childPath = composePaths(
                                        path,
                                        String(index)
                                    );
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
                                        <Draggable
                                            key={index}
                                            draggableId={String(index)}
                                            index={index}
                                        >
                                            {(provided, snapshot) => (
                                                <div
                                                    ref={provided.innerRef}
                                                    {...provided.draggableProps}
                                                >
                                                    <Section
                                                        key={index}
                                                        style={{
                                                            marginBottom: 15,
                                                        }}
                                                        compact
                                                        title={
                                                            <div>
                                                                <span
                                                                    style={{
                                                                        marginRight: 15,
                                                                        cursor: "pointer",
                                                                    }}
                                                                    {...provided.dragHandleProps}
                                                                >
                                                                    <Tooltip
                                                                        content="Drag & drop"
                                                                        minimal
                                                                        placement="bottom-start"
                                                                    >
                                                                        {faIcon(
                                                                            {
                                                                                icon: faArrowUpArrowDown,
                                                                            }
                                                                        )}
                                                                    </Tooltip>
                                                                </span>
                                                                {index + 1}
                                                            </div>
                                                        }
                                                        rightElement={
                                                            snapshot.isDragging ? null : (
                                                                <Popover
                                                                    content={
                                                                        <div
                                                                            style={{
                                                                                maxWidth: 200,
                                                                                padding: 15,
                                                                            }}
                                                                        >
                                                                            <Button
                                                                                intent={
                                                                                    Intent.DANGER
                                                                                }
                                                                                className={
                                                                                    Classes.POPOVER_DISMISS
                                                                                }
                                                                                text="Confirm"
                                                                                onClick={() =>
                                                                                    removeItems(
                                                                                        path,
                                                                                        [
                                                                                            index,
                                                                                        ]
                                                                                    )()
                                                                                }
                                                                            />
                                                                        </div>
                                                                    }
                                                                    placement="bottom-end"
                                                                >
                                                                    <Tooltip
                                                                        minimal
                                                                        placement="bottom-end"
                                                                        content={
                                                                            translations.removeTooltip
                                                                        }
                                                                    >
                                                                        <Button
                                                                            minimal
                                                                            intent={
                                                                                Intent.DANGER
                                                                            }
                                                                            icon={faIcon(
                                                                                {
                                                                                    icon: faTrash,
                                                                                }
                                                                            )}
                                                                        />
                                                                    </Tooltip>
                                                                </Popover>
                                                            )
                                                        }
                                                    >
                                                        {snapshot.isDragging ? null : (
                                                            <SectionCard>
                                                                {content}
                                                            </SectionCard>
                                                        )}
                                                    </Section>
                                                </div>
                                            )}
                                        </Draggable>
                                    );
                                })}
                                {provided.placeholder}
                            </div>
                        )}
                    </StrictModeDroppable>
                </DragDropContext>
            ) : (
                translations.noDataMessage
            )}
            <div>
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
            </div>
        </div>
    );
};
export default withJsonFormsArrayControlProps(ArrayRenderer);
export const ArrayTester = rankWith(5, isObjectArrayWithNesting);

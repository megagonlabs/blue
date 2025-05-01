import { FAIcon } from "@/components/FAIcon";
import {
    faArrowDown,
    faArrowUp,
    faListOl,
    faPlus,
    faTrash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";

const {
    H6,
    Card,
    Tooltip,
    Button,
    ButtonVariant,
    Size,
    Tag,
    Intent,
    ButtonGroup,
    Popover,
    Classes,
    H5,
    H3,
} = require("@blueprintjs/core");
const {
    findUISchema,
    composePaths,
    rankWith,
    isObjectArrayWithNesting,
    createDefaultValue,
} = require("@jsonforms/core");
const {
    JsonFormsDispatch,
    withJsonFormsArrayControlProps,
    withArrayTranslationProps,
    withTranslateProps,
} = require("@jsonforms/react");
const { useMemo, useEffect } = require("react");
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
    const childUiSchema = useMemo(() => {
        return findUISchema(
            uischemas,
            schema,
            uischema.scope,
            path,
            undefined,
            uischema,
            rootSchema
        );
    }, [uischemas, schema, path, uischema, rootSchema]);
    useEffect(() => {}, [data]);
    return (
        <div>
            <H3 style={{ marginTop: 0, marginBottom: 10, lineHeight: "unset" }}>
                {label}
            </H3>
            {!_.isEmpty(data) ? (
                _.range(0, _.size(data)).map((index) => {
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
                        <div
                            className="custom-card"
                            style={{ marginBottom: 10 }}
                        >
                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    padding: "10px 20px 10px 10px",
                                }}
                            >
                                <Tag
                                    minimal
                                    style={{
                                        backgroundColor: "transparent",
                                        fontWeight: 600,
                                    }}
                                    size={Size.LARGE}
                                    intent={Intent.PRIMARY}
                                    icon={
                                        <FAIcon
                                            icon={faListOl}
                                            style={{ marginRight: 10 }}
                                        />
                                    }
                                >
                                    {index + 1}
                                </Tag>
                                <ButtonGroup
                                    variant={ButtonVariant.MINIMAL}
                                    size={Size.LARGE}
                                >
                                    {index > 0 && (
                                        <Tooltip
                                            placement="bottom"
                                            content="Move up"
                                        >
                                            <Button
                                                onClick={() => {
                                                    moveUp(path, index)();
                                                }}
                                                icon={
                                                    <FAIcon icon={faArrowUp} />
                                                }
                                            />
                                        </Tooltip>
                                    )}
                                    {index < _.size(data) - 1 && (
                                        <Tooltip
                                            placement="bottom"
                                            content="Move down"
                                        >
                                            <Button
                                                onClick={() => {
                                                    moveDown(path, index)();
                                                }}
                                                icon={
                                                    <FAIcon
                                                        icon={faArrowDown}
                                                    />
                                                }
                                            />
                                        </Tooltip>
                                    )}
                                    <Popover
                                        placement="bottom-end"
                                        content={
                                            <div style={{ padding: 10 }}>
                                                <Button
                                                    className={
                                                        Classes.POPOVER_DISMISS
                                                    }
                                                    intent={Intent.DANGER}
                                                    onClick={() => {
                                                        removeItems(path, [
                                                            index,
                                                        ])();
                                                    }}
                                                    text="Confirm"
                                                />
                                            </div>
                                        }
                                    >
                                        <Tooltip
                                            content={translations.removeTooltip}
                                            placement="bottom-end"
                                        >
                                            <Button
                                                intent={Intent.DANGER}
                                                icon={<FAIcon icon={faTrash} />}
                                            />
                                        </Tooltip>
                                    </Popover>
                                </ButtonGroup>
                            </div>
                            <div style={{ padding: "0px 20px 20px" }}>
                                {content}
                            </div>
                        </div>
                    );
                })
            ) : (
                <div style={{ marginBottom: 10 }}>
                    {translations.noDataMessage}
                </div>
            )}
            <Tooltip placement="top-start" content={translations.addTooltip}>
                <Button
                    icon={<FAIcon icon={faPlus} />}
                    text="Add"
                    variant={ButtonVariant.OUTLINED}
                    onClick={addItem(
                        path,
                        createDefaultValue(schema, rootSchema)
                    )}
                />
            </Tooltip>
        </div>
    );
};
export default withJsonFormsArrayControlProps(
    withTranslateProps(withArrayTranslationProps(ArrayRenderer))
);
export const ArrayTester = rankWith(5, isObjectArrayWithNesting);

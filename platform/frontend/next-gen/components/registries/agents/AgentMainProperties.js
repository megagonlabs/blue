import { ENTER_KEY_ICON, TAG_REMOVE_ICON } from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import { useAppStore } from "@/stores/app-store";
import {
    Alignment,
    Button,
    ButtonVariant,
    Callout,
    Classes,
    Colors,
    EditableText,
    EntityTitle,
    H3,
    H5,
    InputGroup,
    Intent,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faMemo,
    faPlus,
    faTrash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useCallback, useMemo, useState } from "react";
function Categories({ properties, loading, isEditing, updateMainProperties }) {
    const categories = useMemo(() => {
        return _.isArray(properties.categories) ? properties.categories : [];
    }, [properties.categories]);
    const [entry, setEntry] = useState("");
    const handleRemove = (value) => {
        updateMainProperties({
            path: "categories",
            value: _.without(categories, value),
        });
    };
    const addCategory = (value) => {
        const valueToAdd = _.trim(value);
        if (!_.isEmpty(valueToAdd)) {
            updateMainProperties({
                path: "categories",
                value: _.uniq([...categories, _.trim(value)]),
            });
        }
        setEntry("");
    };
    const handleKeyDown = useCallback(
        (event) => {
            if (_.isEqual(event.key, "Enter")) {
                addCategory(entry);
            }
        },
        [entry]
    );
    return (
        <>
            <H5>Categories</H5>
            <div
                className={loading ? Classes.SKELETON : null}
                style={{
                    marginTop: 10,
                    display: "flex",
                    gap: 10,
                    flexWrap: "wrap",
                }}
            >
                {!isEditing && _.isEmpty(categories) && "-"}
                {categories.map((category) => (
                    <Tag
                        key={category}
                        size={Size.LARGE}
                        minimal
                        endIcon={
                            isEditing ? (
                                <div
                                    onClick={() => {
                                        handleRemove(category);
                                    }}
                                >
                                    {TAG_REMOVE_ICON}
                                </div>
                            ) : null
                        }
                    >
                        {category}
                    </Tag>
                ))}
                {isEditing && (
                    <div style={{ width: 165 }}>
                        <InputGroup
                            rightElement={ENTER_KEY_ICON}
                            placeholder="Press Enter to Add"
                            value={entry}
                            onValueChange={(value) => {
                                setEntry(value);
                            }}
                            onKeyDown={handleKeyDown}
                        />
                    </div>
                )}
            </div>
        </>
    );
}
function InputListeners({
    properties,
    loading,
    isEditing,
    updateMainProperties,
}) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const inputListeners = useMemo(() => {
        return _.isArray(properties.listens) ? properties.listens : [];
    }, [properties.listens]);
    const updateKey = (index, value) => {
        let next = _.cloneDeep(inputListeners);
        _.set(next, [index, "key"], value);
        updateMainProperties({ path: "listens", value: next });
    };
    const removeTag = (index, value, type) => {
        let next = _.cloneDeep(inputListeners);
        let tags = _.get(next, [index, type], []);
        _.set(next, [index, type], _.without(tags, value));
        updateMainProperties({ path: "listens", value: next });
    };
    const [tags, setTags] = useState({});
    const setNewTag = (index, value, type) => {
        let newTags = _.cloneDeep(tags);
        _.set(newTags, [index, type], value);
        setTags(newTags);
    };
    const handleKeyDown = useCallback(
        (event, index, type) => {
            if (_.isEqual(event.key, "Enter")) {
                let next = _.cloneDeep(inputListeners);
                let currentTags = _.get(next, [index, type], []);
                const tagToAdd = _.trim(_.get(tags, [index, type], null));
                if (!_.isEmpty(tagToAdd)) {
                    _.set(
                        next,
                        [index, type],
                        _.uniq([...currentTags, tagToAdd])
                    );
                }
                let nextTags = _.cloneDeep(tags);
                _.set(nextTags, [index, type], "");
                setTags(nextTags);
                updateMainProperties({ path: "listens", value: next });
            }
        },
        [tags]
    );
    const handleRemove = (index) => {
        let next = _.cloneDeep(inputListeners);
        _.pullAt(next, index);
        updateMainProperties({ path: "listens", value: next });
    };
    return (
        <>
            <H5>Input listeners</H5>
            <div
                className={loading ? Classes.SKELETON : null}
                style={{ marginTop: 10 }}
            >
                {!isEditing && _.isEmpty(inputListeners) && "-"}
                {inputListeners.map((inputListener, index) => (
                    <div key={index} style={{ position: "relative" }}>
                        {isEditing && (
                            <div
                                style={{
                                    position: "absolute",
                                    right: 15,
                                    top: 15,
                                }}
                            >
                                <Tooltip placement="left" content="Remove">
                                    <Button
                                        onClick={() => {
                                            handleRemove(index);
                                        }}
                                        intent={Intent.DANGER}
                                        size={Size.LARGE}
                                        variant={ButtonVariant.MINIMAL}
                                        icon={<FAIcon icon={faTrash} />}
                                    />
                                </Tooltip>
                            </div>
                        )}
                        <div
                            style={{
                                marginTop: 10,
                                padding: 15,
                                paddingRight: isEditing ? 70 : 15,
                                backgroundColor: darkMode
                                    ? Colors.DARK_GRAY1
                                    : Colors.LIGHT_GRAY5,
                            }}
                        >
                            {_.isEmpty(_.trim(inputListener.key)) && (
                                <Callout
                                    icon={null}
                                    intent={Intent.WARNING}
                                    style={{ marginBottom: 10 }}
                                >
                                    Input listener with empty input name will be
                                    removed during save.
                                </Callout>
                            )}
                            <div style={{ display: "flex", gap: 10 }}>
                                <div
                                    className={Classes.TEXT_MUTED}
                                    style={{ width: 70 }}
                                >
                                    Input
                                </div>
                                <div style={{ fontWeight: 600 }}>
                                    {isEditing ? (
                                        <EditableText
                                            value={inputListener.key}
                                            onChange={(value) => {
                                                updateKey(index, value);
                                            }}
                                        />
                                    ) : (
                                        inputListener.key
                                    )}
                                </div>
                            </div>
                            {["includes", "excludes"].map((type) => (
                                <div
                                    key={type}
                                    style={{
                                        display: "flex",
                                        gap: 10,
                                        marginTop: 10,
                                    }}
                                >
                                    <div
                                        className={Classes.TEXT_MUTED}
                                        style={{
                                            width: 70,
                                            lineHeight: "30px",
                                        }}
                                    >
                                        {_.capitalize(type)}
                                    </div>
                                    <div
                                        style={{
                                            display: "flex",
                                            gap: 10,
                                            flexWrap: "wrap",
                                        }}
                                    >
                                        {!isEditing &&
                                            _.isEmpty(inputListener[type]) && (
                                                <div
                                                    style={{
                                                        lineHeight: "30px",
                                                    }}
                                                >
                                                    -
                                                </div>
                                            )}
                                        {inputListener[type].map((tag) => (
                                            <Tag
                                                minimal
                                                endIcon={
                                                    isEditing ? (
                                                        <div
                                                            onClick={() => {
                                                                removeTag(
                                                                    index,
                                                                    tag,
                                                                    type
                                                                );
                                                            }}
                                                        >
                                                            {TAG_REMOVE_ICON}
                                                        </div>
                                                    ) : null
                                                }
                                                size={Size.LARGE}
                                                key={tag}
                                            >
                                                {tag}
                                            </Tag>
                                        ))}
                                        {isEditing && (
                                            <div style={{ width: 165 }}>
                                                <InputGroup
                                                    rightElement={
                                                        ENTER_KEY_ICON
                                                    }
                                                    onKeyDown={(event) => {
                                                        handleKeyDown(
                                                            event,
                                                            index,
                                                            type
                                                        );
                                                    }}
                                                    placeholder="Press Enter to Add"
                                                    value={_.get(
                                                        tags,
                                                        [index, type],
                                                        ""
                                                    )}
                                                    onValueChange={(value) => {
                                                        setNewTag(
                                                            index,
                                                            value,
                                                            type
                                                        );
                                                    }}
                                                />
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
                {isEditing && (
                    <Button
                        icon={<FAIcon icon={faPlus} />}
                        style={{
                            marginTop: !_.isEmpty(inputListeners) ? 10 : 0,
                        }}
                        onClick={() => {
                            updateMainProperties({
                                path: "listens",
                                value: [
                                    ...inputListeners,
                                    { key: "", includes: [], excludes: [] },
                                ],
                            });
                        }}
                        fill
                        alignText={Alignment.START}
                        variant={ButtonVariant.MINIMAL}
                        text="Add input listener"
                    />
                )}
            </div>
        </>
    );
}
function OutputTags({ isEditing, loading, properties, updateMainProperties }) {
    const outputTags = useMemo(() => {
        return _.isArray(properties.tags) ? properties.tags : [];
    }, [properties.tags]);
    const [addTags, setAddTags] = useState({});
    const removeTag = (index, tag) => {
        let next = _.cloneDeep(outputTags);
        let tags = _.get(next, [index, "tags"], []);
        _.set(next, [index, "tags"], _.without(tags, tag));
        updateMainProperties({ path: "tags", value: next });
    };
    const updateKey = (index, value) => {
        let next = _.cloneDeep(outputTags);
        _.set(next, [index, "key"], value);
        updateMainProperties({ path: "tags", value: next });
    };
    const handleKeyDown = useCallback(
        (event, index) => {
            if (_.isEqual(event.key, "Enter")) {
                let next = _.cloneDeep(outputTags);
                let currentTags = _.get(next, [index, "tags"], []);
                const tagToAdd = _.trim(_.get(addTags, index, null));
                if (!_.isEmpty(tagToAdd)) {
                    _.set(
                        next,
                        [index, "tags"],
                        _.uniq([...currentTags, tagToAdd])
                    );
                }
                let nextAddTags = _.cloneDeep(addTags);
                _.set(nextAddTags, index, "");
                setAddTags(nextAddTags);
                updateMainProperties({ path: "tags", value: next });
            }
        },
        [addTags]
    );
    const updateAddTag = (index, tag) => {
        let newAddTags = _.cloneDeep(addTags);
        _.set(newAddTags, index, tag);
        setAddTags(newAddTags);
    };
    const handleRemove = (index) => {
        let next = _.cloneDeep(outputTags);
        _.pullAt(next, index);
        updateMainProperties({ path: "tags", value: next });
    };
    const darkMode = useAppStore((state) => state.dark_mode);
    return (
        <>
            <H5>Output tags</H5>
            <div
                className={loading ? Classes.SKELETON : null}
                style={{ marginTop: 10 }}
            >
                {!isEditing && _.isEmpty(outputTags) && "-"}
                {outputTags.map((outputTag, index) => (
                    <div key={index} style={{ position: "relative" }}>
                        {isEditing && (
                            <div
                                style={{
                                    position: "absolute",
                                    right: 15,
                                    top: 15,
                                }}
                            >
                                <Tooltip placement="left" content="Remove">
                                    <Button
                                        onClick={() => {
                                            handleRemove(index);
                                        }}
                                        intent={Intent.DANGER}
                                        size={Size.LARGE}
                                        variant={ButtonVariant.MINIMAL}
                                        icon={<FAIcon icon={faTrash} />}
                                    />
                                </Tooltip>
                            </div>
                        )}
                        <div
                            style={{
                                marginTop: 10,
                                padding: 15,
                                paddingRight: isEditing ? 70 : 15,
                                backgroundColor: darkMode
                                    ? Colors.DARK_GRAY1
                                    : Colors.LIGHT_GRAY5,
                            }}
                        >
                            {_.isEmpty(_.trim(outputTag.key)) && (
                                <Callout
                                    icon={null}
                                    intent={Intent.WARNING}
                                    style={{ marginBottom: 10 }}
                                >
                                    Output tag with empty output name will be
                                    removed during save.
                                </Callout>
                            )}
                            <div style={{ display: "flex", gap: 10 }}>
                                <div
                                    className={Classes.TEXT_MUTED}
                                    style={{ width: 70 }}
                                >
                                    Output
                                </div>
                                <div style={{ fontWeight: 600 }}>
                                    {isEditing ? (
                                        <EditableText
                                            value={outputTag.key}
                                            onChange={(value) => {
                                                updateKey(index, value);
                                            }}
                                        />
                                    ) : (
                                        outputTag.key
                                    )}
                                </div>
                            </div>
                            <div
                                style={{
                                    display: "flex",
                                    gap: 10,
                                    marginTop: 10,
                                }}
                            >
                                <div
                                    className={Classes.TEXT_MUTED}
                                    style={{
                                        width: 70,
                                        lineHeight: "30px",
                                    }}
                                >
                                    Tags
                                </div>
                                <div
                                    style={{
                                        display: "flex",
                                        gap: 10,
                                        flexWrap: "wrap",
                                    }}
                                >
                                    {!isEditing &&
                                        _.isEmpty(outputTag.tags) && (
                                            <div
                                                style={{
                                                    lineHeight: "30px",
                                                }}
                                            >
                                                -
                                            </div>
                                        )}
                                    {outputTag.tags.map((tag) => (
                                        <Tag
                                            minimal
                                            size={Size.LARGE}
                                            key={tag}
                                            endIcon={
                                                isEditing ? (
                                                    <div
                                                        onClick={() => {
                                                            removeTag(
                                                                index,
                                                                tag
                                                            );
                                                        }}
                                                    >
                                                        {TAG_REMOVE_ICON}
                                                    </div>
                                                ) : null
                                            }
                                        >
                                            {tag}
                                        </Tag>
                                    ))}
                                    {isEditing && (
                                        <div style={{ width: 165 }}>
                                            <InputGroup
                                                rightElement={ENTER_KEY_ICON}
                                                onKeyDown={(event) => {
                                                    handleKeyDown(event, index);
                                                }}
                                                placeholder="Press Enter to Add"
                                                value={_.get(
                                                    addTags,
                                                    index,
                                                    ""
                                                )}
                                                onValueChange={(value) => {
                                                    updateAddTag(index, value);
                                                }}
                                            />
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
                {isEditing && (
                    <Button
                        icon={<FAIcon icon={faPlus} />}
                        style={{
                            marginTop: !_.isEmpty(outputTags) ? 10 : 0,
                        }}
                        onClick={() => {
                            updateMainProperties({
                                path: "tags",
                                value: [...outputTags, { key: "", tags: [] }],
                            });
                        }}
                        fill
                        alignText={Alignment.START}
                        variant={ButtonVariant.MINIMAL}
                        text="Add output tag"
                    />
                )}
            </div>
        </>
    );
}
export default function AgentMainProperties({
    isEditing,
    loading,
    properties,
    updateMainProperties,
}) {
    return (
        <div>
            <div style={{ marginBottom: 10 }}>
                <EntityTitle
                    icon={<FAIcon icon={faMemo} size={25} />}
                    heading={H3}
                    title="Main"
                />
            </div>
            <Categories
                updateMainProperties={updateMainProperties}
                isEditing={isEditing}
                properties={properties}
                loading={loading}
            />
        </div>
    );
}

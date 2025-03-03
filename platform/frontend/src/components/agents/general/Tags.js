import { faIcon } from "@/components/icon";
import {
    Button,
    Classes,
    Colors,
    EditableText,
    FormGroup,
    Intent,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { faPlus, faTrash } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useEffect, useState } from "react";
export default function Tags({
    edit,
    general,
    loading,
    setGeneral,
    X_MARK_ICON,
    setEdit,
}) {
    const [entries, setEntries] = useState([]);
    useEffect(() => {
        if (_.isArray(general.tags)) setEntries(general.tags);
    }, [general.tags]);
    useEffect(() => {
        if (!_.isEqual(entries, general.tags)) {
            setGeneral({ ...general, tags: entries });
        }
    }, [entries]);
    const updateKey = (index, key) => {
        let newEntries = _.cloneDeep(entries);
        _.set(newEntries, [index, "key"], key);
        setEntries(newEntries);
    };
    const updateEntry = (operation, index = -1) => {
        let newEntries = _.cloneDeep(entries);
        if (_.isEqual(operation, "remove")) {
            _.pullAt(newEntries, index);
        } else if (_.isEqual(operation, "add")) {
            newEntries.push({ key: "DEFAULT", tags: [] });
        }
        setEntries(newEntries);
    };
    const updateTag = (index, tag, type, operation) => {
        let newEntries = _.cloneDeep(entries);
        let tags = _.get(newEntries, [index, type], []);
        if (_.isEqual(operation, "remove")) {
            tags = _.without(tags, tag);
        } else if (_.isEqual(operation, "add")) {
            if (!_.includes(tags, tag)) tags.push(tag);
        }
        _.set(newEntries, [index, type], tags);
        setEntries(newEntries);
    };
    const [addTags, setAddTags] = useState({});
    const updateAddTag = (index, tag) => {
        let newAddTags = _.cloneDeep(addTags);
        _.set(newAddTags, index, tag);
        setAddTags(newAddTags);
    };
    return (
        <FormGroup
            className="margin-0"
            label={<div style={{ fontWeight: 600 }}>Tags</div>}
        >
            {_.isEmpty(entries) && !edit && (
                <div className={loading ? Classes.SKELETONL : null}>-</div>
            )}
            {entries.map((entry, index) => {
                return (
                    <div
                        key={index}
                        onDoubleClick={() => setEdit(true)}
                        style={{
                            position: "relative",
                            marginTop: index > 0 ? 7.5 : 0,
                            padding: "15px 70px 15px 15px",
                            borderRadius: 2,
                            backgroundColor: Colors.LIGHT_GRAY5,
                        }}
                    >
                        {edit && (
                            <div
                                className={loading ? Classes.SKELETON : null}
                                style={{ position: "absolute", right: 15 }}
                            >
                                <Tooltip
                                    placement="bottom-end"
                                    content="Remove"
                                    minimal
                                >
                                    <Button
                                        intent={Intent.DANGER}
                                        size="large"
                                        variant="minimal"
                                        onClick={() =>
                                            updateEntry("remove", index)
                                        }
                                        icon={faIcon({ icon: faTrash })}
                                    />
                                </Tooltip>
                            </div>
                        )}
                        <div
                            style={{
                                marginBottom: 7.5,
                                display: "flex",
                                alignItems: "center",
                            }}
                        >
                            <div
                                style={{ minWidth: 70 }}
                                className={Classes.TEXT_MUTED}
                            >
                                Output
                            </div>
                            {edit ? (
                                <EditableText
                                    className={
                                        loading ? Classes.SKELETON : null
                                    }
                                    value={entry.key}
                                    onChange={(value) =>
                                        updateKey(index, value)
                                    }
                                />
                            ) : _.isEmpty(entry.key) ? (
                                "-"
                            ) : (
                                entry.key
                            )}
                        </div>
                        <div style={{ display: "flex" }}>
                            <div
                                style={{ minWidth: 70, lineHeight: "30px" }}
                                className={Classes.TEXT_MUTED}
                            >
                                Tags
                            </div>
                            <div
                                style={{
                                    flexWrap: "wrap",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 7.5,
                                }}
                            >
                                {_.isEmpty(entry.tags) && !edit && "-"}
                                {entry.tags.map((tag, tagIndex) => (
                                    <Tag
                                        size="large"
                                        className={
                                            loading ? Classes.SKELETON : null
                                        }
                                        key={tagIndex}
                                        minimal
                                        endIcon={
                                            edit && (
                                                <div
                                                    style={{
                                                        width: 16,
                                                        cursor: "pointer",
                                                    }}
                                                    onClick={() =>
                                                        updateTag(
                                                            index,
                                                            tag,
                                                            "tags",
                                                            "remove"
                                                        )
                                                    }
                                                >
                                                    {X_MARK_ICON}
                                                </div>
                                            )
                                        }
                                    >
                                        {tag}
                                    </Tag>
                                ))}
                                {edit && !loading && (
                                    <EditableText
                                        placeholder="Add"
                                        value={_.get(addTags, index, "")}
                                        onConfirm={(value) => {
                                            if (_.isEmpty(value)) return;
                                            updateTag(
                                                index,
                                                value,
                                                "tags",
                                                "add"
                                            );
                                            updateAddTag(index, "");
                                        }}
                                        onChange={(value) =>
                                            updateAddTag(index, value)
                                        }
                                        selectAllOnFocus
                                    />
                                )}
                            </div>
                        </div>
                    </div>
                );
            })}
            {edit && !loading && (
                <Button
                    onClick={() => updateEntry("add")}
                    style={{ marginTop: !_.isEmpty(entries) > 0 ? 7.5 : 0 }}
                    variant="outlined"
                    icon={faIcon({ icon: faPlus })}
                    text="Add tag"
                />
            )}
        </FormGroup>
    );
}

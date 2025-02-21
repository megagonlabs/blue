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
import {
    faPlus,
    faTrash,
    faXmark,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useEffect, useState } from "react";
export default function Listens({ edit, general, loading, setGeneral }) {
    const [entries, setEntries] = useState([]);
    useEffect(() => {
        if (_.isArray(general.listens)) setEntries(general.listens);
    }, [general.listens]);
    useEffect(() => {
        if (!_.isEqual(entries, general.listens)) {
            setGeneral({ ...general, listens: entries });
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
            newEntries.push({ key: "", includes: [], excludes: [] });
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
    const X_MARK_ICON = faIcon({
        icon: faXmark,
        style: { position: "absolute", top: 7 },
    });
    const [addTags, setAddTags] = useState({});
    const updateAddTag = (index, tag, type) => {
        let newAddTags = _.cloneDeep(addTags);
        _.set(newAddTags, [index, type], tag);
        setAddTags(newAddTags);
    };
    return (
        <FormGroup
            className="margin-0"
            label={<div className={Classes.TEXT_MUTED}>Listens</div>}
        >
            {_.isEmpty(entries) && !edit && (
                <div className={loading ? Classes.SKELETON : null}>-</div>
            )}
            {entries.map((entry, index) => {
                return (
                    <div
                        key={index}
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
                                        large
                                        minimal
                                        onClick={() =>
                                            updateEntry("remove", index)
                                        }
                                        icon={faIcon({ icon: faTrash })}
                                    />
                                </Tooltip>
                            </div>
                        )}
                        <div style={{ marginBottom: 7.5 }}>
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
                        <div style={{ marginBottom: 7.5, display: "flex" }}>
                            <div
                                style={{ minWidth: 70, lineHeight: "30px" }}
                                className={Classes.TEXT_MUTED}
                            >
                                Includes
                            </div>
                            <div
                                style={{
                                    flexWrap: "wrap",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 7.5,
                                }}
                            >
                                {_.isEmpty(entry.includes) && !edit && "-"}
                                {entry.includes.map((tag, tagIndex) => (
                                    <Tag
                                        large
                                        className={
                                            loading ? Classes.SKELETON : null
                                        }
                                        key={tagIndex}
                                        minimal
                                        rightIcon={
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
                                                            "includes",
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
                                        value={_.get(
                                            addTags,
                                            [index, "includes"],
                                            ""
                                        )}
                                        onConfirm={(value) => {
                                            if (_.isEmpty(value)) return;
                                            updateTag(
                                                index,
                                                value,
                                                "includes",
                                                "add"
                                            );
                                            updateAddTag(index, "", "includes");
                                        }}
                                        onChange={(value) =>
                                            updateAddTag(
                                                index,
                                                value,
                                                "includes"
                                            )
                                        }
                                        selectAllOnFocus
                                    />
                                )}
                            </div>
                        </div>
                        <div style={{ display: "flex" }}>
                            <div
                                style={{ minWidth: 70, lineHeight: "30px" }}
                                className={Classes.TEXT_MUTED}
                            >
                                Excludes
                            </div>
                            <div
                                style={{
                                    flexWrap: "wrap",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 7.5,
                                }}
                            >
                                {_.isEmpty(entry.excludes) && !edit && "-"}
                                {entry.excludes.map((tag, tagIndex) => (
                                    <Tag
                                        large
                                        className={
                                            loading ? Classes.SKELETON : null
                                        }
                                        key={tagIndex}
                                        minimal
                                        rightIcon={
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
                                                            "excludes",
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
                                        value={_.get(
                                            addTags,
                                            [index, "excludes"],
                                            ""
                                        )}
                                        onConfirm={(value) => {
                                            if (_.isEmpty(value)) return;
                                            updateTag(
                                                index,
                                                value,
                                                "excludes",
                                                "add"
                                            );
                                            updateAddTag(index, "", "excludes");
                                        }}
                                        onChange={(value) =>
                                            updateAddTag(
                                                index,
                                                value,
                                                "excludes"
                                            )
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
                    outlined
                    icon={faIcon({ icon: faPlus })}
                    text="Add tag"
                />
            )}
        </FormGroup>
    );
}

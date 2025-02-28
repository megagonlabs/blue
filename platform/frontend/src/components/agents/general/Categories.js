import { Classes, EditableText, FormGroup, Tag } from "@blueprintjs/core";
import _ from "lodash";
import { useEffect, useState } from "react";
export default function Categories({
    edit,
    general,
    loading,
    setGeneral,
    X_MARK_ICON,
    setEdit,
}) {
    const [entries, setEntries] = useState([]);
    useEffect(() => {
        if (
            _.isArray(general.categories) &&
            !_.isEqual(entries, general.categories)
        )
            setEntries(general.categories);
    }, [general.categories]);
    useEffect(() => {
        if (!_.isEqual(entries, general.categories)) {
            setGeneral({ ...general, categories: entries });
        }
    }, [entries]);
    const updateCategory = (category, operation) => {
        let newEntries = _.cloneDeep(entries);
        if (_.isEqual(operation, "remove")) {
            newEntries = _.without(newEntries, category);
        } else if (_.isEqual(operation, "add")) {
            if (!_.includes(newEntries, category)) newEntries.push(category);
        }
        setEntries(newEntries);
    };
    const [addCategory, setAddCategory] = useState("");
    return (
        <FormGroup
            className="margin-0"
            label={<div style={{ fontWeight: 600 }}>Categories</div>}
        >
            {_.isEmpty(entries) && !edit && (
                <div className={loading ? Classes.SKELETONL : null}>-</div>
            )}
            <div
                style={{
                    flexWrap: "wrap",
                    display: "flex",
                    gap: 7.5,
                    alignItems: "center",
                }}
            >
                {entries.map((entry, index) => (
                    <Tag
                        className={loading ? Classes.SKELETON : null}
                        key={index}
                        size="large"
                        minimal
                        endIcon={
                            edit && (
                                <div
                                    style={{
                                        width: 16,
                                        cursor: "pointer",
                                    }}
                                    onClick={() =>
                                        updateCategory(entry, "remove")
                                    }
                                >
                                    {X_MARK_ICON}
                                </div>
                            )
                        }
                    >
                        {entry}
                    </Tag>
                ))}
                {edit && !loading && (
                    <EditableText
                        placeholder="Add"
                        value={addCategory}
                        onConfirm={(value) => {
                            if (_.isEmpty(value)) return;
                            updateCategory(value, "add");
                            setAddCategory("");
                        }}
                        onChange={(value) => setAddCategory(value)}
                        selectAllOnFocus
                    />
                )}
            </div>
        </FormGroup>
    );
}

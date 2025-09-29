import { ENTER_KEY_ICON, TAG_REMOVE_ICON } from "@/components/constants";
import { Classes, H5, InputGroup, Size, Tag } from "@blueprintjs/core";
import _ from "lodash";
import { useCallback, useMemo, useState } from "react";
export default function Categories({
    properties,
    loading,
    isEditing,
    updateMainProperties,
}) {
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

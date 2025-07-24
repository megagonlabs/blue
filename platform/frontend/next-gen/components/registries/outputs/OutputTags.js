import { ENTER_KEY_ICON, TAG_REMOVE_ICON } from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import {
    Classes,
    EntityTitle,
    H3,
    InputGroup,
    Size,
    Tag,
} from "@blueprintjs/core";
import { faTags } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useCallback, useMemo, useState } from "react";
export default function OutputTags({
    isEditing,
    loading,
    properties,
    updateMainProperties,
}) {
    const tags = useMemo(() => {
        return _.get(properties, "tags", []);
    }, [properties.tags]);
    const [entry, setEntry] = useState("");
    const handleRemove = (value) => {
        updateMainProperties({
            path: "tags",
            value: _.without(tags, value),
        });
    };
    const addTag = (value) => {
        const valueToAdd = _.trim(value);
        if (!_.isEmpty(valueToAdd)) {
            updateMainProperties({
                path: "tags",
                value: _.uniq([...tags, valueToAdd]),
            });
        }
        setEntry("");
    };
    const handleKeyDown = useCallback(
        (event) => {
            if (_.isEqual(event.key, "Enter")) {
                addTag(entry);
            }
        },
        [entry]
    );
    return (
        <div>
            <div style={{ marginBottom: 10 }}>
                <EntityTitle
                    icon={<FAIcon icon={faTags} size={25} />}
                    heading={H3}
                    title="Tags"
                />
            </div>
            <div
                className={loading ? Classes.SKELETON : null}
                style={{
                    marginTop: 10,
                    display: "flex",
                    gap: 10,
                    flexWrap: "wrap",
                }}
            >
                {!isEditing && _.isEmpty(tags) && "-"}
                {tags.map((tag) => (
                    <Tag
                        key={tag}
                        size={Size.LARGE}
                        minimal
                        endIcon={
                            isEditing ? (
                                <div
                                    onClick={() => {
                                        handleRemove(tag);
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
        </div>
    );
}

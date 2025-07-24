import { ENTER_KEY_ICON, TAG_REMOVE_ICON } from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import {
    Classes,
    EntityTitle,
    H3,
    H5,
    InputGroup,
    Size,
    Tag,
} from "@blueprintjs/core";
import { faEarListen } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useCallback, useMemo, useState } from "react";
export default function InputListens({
    isEditing,
    loading,
    properties,
    updateMainProperties,
}) {
    const listens = useMemo(() => {
        let result = _.get(properties, "listens", {});
        if (_.isEmpty(_.get(result, "includes", []))) {
            delete result.includes;
        }
        if (_.isEmpty(_.get(result, "excludes", []))) {
            delete result.excludes;
        }
        return result;
    }, [properties.listens]);
    const [includeEntry, setIncludeEntry] = useState("");
    const [excludeEntry, setExcludeEntry] = useState("");
    const handleRemove = (value, type) => {
        let result = _.cloneDeep(listens);
        let tags = _.without(_.get(result, type, []), value);
        _.set(result, type, tags);
        updateMainProperties({
            path: "listens",
            value: result,
        });
    };
    const addTag = (value, type) => {
        const valueToAdd = _.trim(value);
        if (!_.isEmpty(valueToAdd)) {
            let result = _.cloneDeep(listens);
            let tags = _.uniq([..._.get(result, type, []), valueToAdd]);
            _.set(result, type, tags);
            updateMainProperties({
                path: "listens",
                value: result,
            });
        }
        if (_.isEqual(type, "includes")) {
            setIncludeEntry("");
        } else if (_.isEqual(type, "excludes")) {
            setExcludeEntry("");
        }
    };
    const handleKeyDown = useCallback(
        (event, type) => {
            if (_.isEqual(event.key, "Enter")) {
                if (_.isEqual(type, "includes")) {
                    addTag(includeEntry, type);
                } else if (_.isEqual(type, "excludes")) {
                    addTag(excludeEntry, type);
                }
            }
        },
        [includeEntry, excludeEntry]
    );
    return (
        <div>
            <div style={{ marginBottom: 10 }}>
                <EntityTitle
                    icon={<FAIcon icon={faEarListen} size={25} />}
                    heading={H3}
                    title="Listens"
                />
            </div>
            {!isEditing && _.isEmpty(listens) && "-"}
            <div className="split-pane-container">
                {["includes", "excludes"].map((type, index) => (
                    <div className="pane-item" key={index}>
                        <H5>{_.capitalize(type)}</H5>
                        <div
                            className={loading ? Classes.SKELETON : null}
                            style={{
                                marginTop: 10,
                                display: "flex",
                                gap: 10,
                                flexWrap: "wrap",
                            }}
                        >
                            {_.get(listens, type, []).map((tag) => (
                                <Tag
                                    key={tag}
                                    size={Size.LARGE}
                                    minimal
                                    endIcon={
                                        isEditing ? (
                                            <div
                                                onClick={() => {
                                                    handleRemove(tag, type);
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
                                        value={
                                            _.isEqual(type, "includes")
                                                ? includeEntry
                                                : _.isEqual(type, "excludes")
                                                ? excludeEntry
                                                : null
                                        }
                                        onValueChange={(value) => {
                                            if (_.isEqual(type, "includes")) {
                                                setIncludeEntry(value);
                                            } else if (
                                                _.isEqual(type, "excludes")
                                            ) {
                                                setExcludeEntry(value);
                                            }
                                        }}
                                        onKeyDown={(event) => {
                                            handleKeyDown(event, type);
                                        }}
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

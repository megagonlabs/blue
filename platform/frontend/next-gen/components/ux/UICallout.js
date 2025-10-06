import { useUIVisibilityStore } from "@/stores/ui-visibility-store";
import { Callout, Checkbox, Classes, Colors } from "@blueprintjs/core";
import { faUserQuestion } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useState } from "react";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../FAIcon";
export function UICallout({ content, id }) {
    const { UIVisibility, setVisibility, queue } = useUIVisibilityStore(
        useShallow((state) => ({
            UIVisibility: state.UIVisibility,
            setVisibility: state.setVisibility,
            queue: state.queue,
        }))
    );
    const onChange = (event) => {
        setVisibility({ id, value: !event.target.checked });
    };
    const [isOpen, setIsOpen] = useState(false);
    if (!_.get(UIVisibility, id, true)) {
        return null;
    }
    return (
        <Callout
            icon={null}
            style={!isOpen ? { width: "fit-content", cursor: "pointer" } : null}
            onClick={() => {
                setIsOpen(true);
            }}
        >
            <div style={{ display: "flex", gap: 10, lineHeight: "20px" }}>
                <FAIcon
                    icon={faUserQuestion}
                    size={20}
                    style={{ color: Colors.ORANGE3 }}
                />
                {isOpen ? (
                    <div>
                        {content}
                        {!_.isEmpty(id) && (
                            <div>
                                <Checkbox
                                    className={
                                        _.get(queue, id, false) &&
                                        Classes.SKELETON
                                    }
                                    onChange={onChange}
                                    checked={!_.get(UIVisibility, id, true)}
                                    style={{ marginBottom: 0, marginTop: 10 }}
                                    label="Don't show this again"
                                />
                            </div>
                        )}
                    </div>
                ) : (
                    "Tip"
                )}
            </div>
        </Callout>
    );
}

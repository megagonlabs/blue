import { useUIVisibilityStore } from "@/stores/ui-visibility-store";
import {
    Callout,
    Checkbox,
    Classes,
    Colors,
    Popover,
    Tooltip,
} from "@blueprintjs/core";
import { faUserQuestion } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useRef } from "react";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../FAIcon";
import {
    POPOVER_CONTENT_MAX_WIDTH,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "../constants";
export default function UITip({ content, id }) {
    const { UIVisibility, setVisibility, queue } = useUIVisibilityStore(
        useShallow((state) => ({
            UIVisibility: state.UIVisibility,
            setVisibility: state.setVisibility,
            queue: state.queue,
        }))
    );
    const elementRef = useRef(null);
    const popoverBoundary =
        elementRef.current &&
        elementRef.current.closest(".grid-container-boundary");
    const onChange = (event) => {
        setVisibility({ id, value: !event.target.checked });
    };
    if (!_.get(UIVisibility, id, true)) {
        return null;
    }
    return (
        <div ref={elementRef}>
            <Popover
                {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                boundary={popoverBoundary}
                content={
                    <div style={{ padding: 10, lineHeight: "20px" }}>
                        <Callout icon={null}>
                            <div
                                style={{
                                    display: "flex",
                                    gap: 10,
                                    lineHeight: "20px",
                                    maxWidth: POPOVER_CONTENT_MAX_WIDTH,
                                }}
                            >
                                <FAIcon
                                    icon={faUserQuestion}
                                    size={20}
                                    style={{ color: Colors.ORANGE3 }}
                                />
                                {content}
                            </div>
                            <div style={{ marginLeft: 30 }}>
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
                        </Callout>
                    </div>
                }
            >
                <Tooltip
                    {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                    content="Tip"
                    boundary={popoverBoundary}
                    placement="bottom"
                    openOnTargetFocus={false}
                >
                    <FAIcon
                        size={20}
                        icon={faUserQuestion}
                        style={{ color: Colors.ORANGE3, cursor: "pointer" }}
                    />
                </Tooltip>
            </Popover>
        </div>
    );
}

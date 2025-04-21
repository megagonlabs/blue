import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    NonIdealState,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import { faBan, faLampDesk } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useRef } from "react";
import { FAIcon } from "../FAIcon";
import { POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10 } from "../constants";
import WorkspaceMessage from "./workspace/WorkspaceMessage";
export default function Workspace({ sessionId }) {
    const elementRef = useRef(null);
    const popoverBoundary =
        elementRef.current &&
        elementRef.current.closest(".grid-container-boundary");
    const contents = useSessionStore((state) =>
        _.get(state, ["sessions", sessionId, "workspace"], [])
    );
    if (_.isEmpty(contents)) {
        return (
            <NonIdealState
                icon={<FAIcon icon={faLampDesk} size={50} />}
                title="Workspace"
            />
        );
    }
    return (
        <>
            <div
                ref={elementRef}
                className="border-bottom"
                style={{ padding: 10 }}
            >
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    <Tooltip
                        {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                        content="Clear workspace"
                        boundary={popoverBoundary}
                    >
                        <Button
                            icon={
                                <FAIcon
                                    icon={faBan}
                                    className="fa-rotate-by"
                                    style={{ "--fa-rotate-angle": "90deg" }}
                                />
                            }
                        />
                    </Tooltip>
                </ButtonGroup>
            </div>
            <div
                className="full-parent-dimension"
                style={{
                    maxHeight: "calc(100% - 61px)",
                    overflowY: "auto",
                    padding: "10px 20px",
                }}
            >
                {contents.map((content, index) => {
                    const { type } = content;
                    if (_.isEqual(type, "session")) {
                        return (
                            <div
                                key={index}
                                style={{ marginTop: index > 0 ? 20 : 0 }}
                            >
                                <WorkspaceMessage
                                    sessionId={sessionId}
                                    content={content}
                                    index={index}
                                />
                            </div>
                        );
                    }
                    return null;
                })}
            </div>
        </>
    );
}

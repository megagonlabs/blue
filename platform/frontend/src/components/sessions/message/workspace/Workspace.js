import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import MessageSnapshot from "@/components/sessions/message/workspace/MessageSnapshot";
import {
    Button,
    ButtonGroup,
    Callout,
    Divider,
    Intent,
    NonIdealState,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowsToLine,
    faBan,
    faLampDesk,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext, useRef } from "react";
export default function Workspace() {
    const { appState, appActions } = useContext(AppContext);
    const { sessionWorkspace, sessionIdFocus } = appState.session;
    const hasError = useRef(false);
    const contents = _.get(sessionWorkspace, sessionIdFocus, []);
    if (_.isEmpty(contents)) {
        return (
            <NonIdealState
                icon={faIcon({ icon: faLampDesk, size: 50 })}
                title="Workspace"
            />
        );
    }
    return (
        <div className="full-parent-height">
            <div
                className="bp-border-bottom"
                style={{ padding: "5px 20px", marginTop: 1 }}
            >
                <ButtonGroup minimal>
                    <Tooltip
                        minimal
                        content="Clear workspace"
                        placement="bottom-start"
                    >
                        <Button
                            onClick={() =>
                                appActions.session.clearCurrentWorkspace()
                            }
                            icon={faIcon({
                                icon: faBan,
                                className: "fa-rotate-by",
                                style: { "--fa-rotate-angle": "90deg" },
                            })}
                        />
                    </Tooltip>
                    <Divider />
                    <Tooltip content="Collapse all" minimal placement="bottom">
                        <Button
                            icon={faIcon({ icon: faArrowsToLine })}
                            minimal
                        />
                    </Tooltip>
                </ButtonGroup>
            </div>
            <div
                style={{
                    padding: 20,
                    overflowY: "auto",
                    height: "calc(100% - 41px)",
                }}
            >
                {contents.map((content, index) => {
                    const { type } = content;
                    if (!hasError.current) {
                        if (_.isEqual(type, "session")) {
                            return (
                                <div
                                    key={index}
                                    style={{ marginTop: index > 0 ? 20 : 0 }}
                                >
                                    <MessageSnapshot
                                        hasError={hasError}
                                        index={index}
                                        content={content}
                                    />
                                </div>
                            );
                        }
                    }
                    return (
                        <div key={index}>
                            <Callout
                                style={{ marginTop: index > 0 ? 20 : 0 }}
                                intent={Intent.DANGER}
                                icon={null}
                                title="Unable to display the content"
                            >
                                We&apos;re unable to read the source data of
                                this content
                            </Callout>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

import { AppContext } from "@/components/contexts/app-context";
import { sendSocketMessage } from "@/components/helper";
import { useSocket } from "@/components/hooks/useSocket";
import { faIcon } from "@/components/icon";
import SessionList from "@/components/sessions/SessionList";
import { Button, ButtonGroup, Tooltip } from "@blueprintjs/core";
import { faBell } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext, useEffect, useRef } from "react";
export default function Sessions() {
    const { appState, appActions } = useContext(AppContext);
    const { unreadSessionIds, sessionListPanelCollapsed } = appState.session;
    const { socket, isSocketOpen } = useSocket();
    const initialFetchAll = useRef(true);
    useEffect(() => {
        if (!isSocketOpen) return;
        if (initialFetchAll.current) {
            initialFetchAll.current = false;
            sendSocketMessage(
                socket,
                JSON.stringify({ type: "REQUEST_USER_AGENT_ID" })
            );
        }
    }, [isSocketOpen]); // eslint-disable-line react-hooks/exhaustive-deps
    return (
        <>
            <div>
                {!sessionListPanelCollapsed ? (
                    <div className="full-parent-height">
                        <div
                            className="border-top border-right"
                            style={{
                                padding: "5px 20px",
                                borderRadius: 0,
                            }}
                        >
                            <ButtonGroup fill minimal>
                                <Button
                                    text="All"
                                    onClick={() => {
                                        appActions.session.setState({
                                            key: "sessionGroupBy",
                                            value: "all",
                                        });
                                    }}
                                    active={_.isEqual(
                                        appState.session.sessionGroupBy,
                                        "all"
                                    )}
                                />
                                <Button
                                    text="Pinned"
                                    onClick={() => {
                                        appActions.session.setState({
                                            key: "sessionGroupBy",
                                            value: "pinned",
                                        });
                                    }}
                                    active={_.isEqual(
                                        appState.session.sessionGroupBy,
                                        "pinned"
                                    )}
                                />
                                <Button
                                    text="Owner"
                                    onClick={() => {
                                        appActions.session.setState({
                                            key: "sessionGroupBy",
                                            value: "owner",
                                        });
                                    }}
                                    active={_.isEqual(
                                        appState.session.sessionGroupBy,
                                        "owner"
                                    )}
                                />
                                <Button
                                    text="Member"
                                    onClick={() => {
                                        appActions.session.setState({
                                            key: "sessionGroupBy",
                                            value: "member",
                                        });
                                    }}
                                    active={_.isEqual(
                                        appState.session.sessionGroupBy,
                                        "member"
                                    )}
                                />
                            </ButtonGroup>
                        </div>
                        <SessionList />
                    </div>
                ) : (
                    <div
                        className="full-parent-height border-right"
                        style={{ padding: 20 }}
                    >
                        {!_.isEmpty(unreadSessionIds) ? (
                            <Tooltip
                                minimal
                                placement="right"
                                content={`${_.size(
                                    unreadSessionIds
                                )} unread session${
                                    _.size(unreadSessionIds) > 1 ? "s" : ""
                                }`}
                            >
                                <Button
                                    style={{ cursor: "initial" }}
                                    large
                                    minimal
                                    icon={faIcon({ icon: faBell })}
                                />
                            </Tooltip>
                        ) : null}
                    </div>
                )}
            </div>
        </>
    );
}

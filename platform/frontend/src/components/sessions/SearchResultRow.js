import { faIcon } from "@/components/icon";
import SessionMemberStack from "@/components/sessions/SessionMemberStack";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
    Card,
    Classes,
    H5,
    Tooltip,
} from "@blueprintjs/core";
import {
    faClipboard,
    faCopy,
    faThumbTack,
    faThumbTackSlash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useRouter } from "next/router";
import { useContext, useState } from "react";
import { AppContext } from "../contexts/app-context";
import { useSocket } from "../hooks/useSocket";
export default function SearchResultRow({ sessionId, style = {} }) {
    const { appState, appActions } = useContext(AppContext);
    const { pinnedSessionIds, sessionDetails } = appState.session;
    const sessionName = _.get(sessionDetails, [sessionId, "name"], sessionId);
    const sessionDescription = _.get(
        sessionDetails,
        [sessionId, "description"],
        ""
    );
    const router = useRouter();
    const { socket } = useSocket();
    const [updatingPin, setUpdatingPin] = useState(false);
    const isPinned = pinnedSessionIds.has(sessionId);
    const handlePinSession = () => {
        setUpdatingPin(true);
        axios
            .put(`/sessions/session/${sessionId}/${isPinned ? "un" : ""}pin`)
            .then(() => {
                if (isPinned)
                    appActions.session.removePinnedSessionId(sessionId);
                else appActions.session.addPinnedSessionId(sessionId);
                AppToaster.show({
                    icon: faIcon({ icon: faThumbTack }),
                    message: `${
                        isPinned ? "Unpinned" : "Pinned"
                    } "${sessionName}"`,
                });
            })
            .finally(() => setUpdatingPin(false));
    };
    return (
        <div style={style}>
            <Card
                className="session-search-result-row"
                onClick={() => {
                    appActions.session.setSessionIdFocus(sessionId);
                    appActions.session.observeSession({
                        sessionId,
                        socket,
                    });
                    router.push("/sessions");
                }}
                style={{
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    padding: "18px 20px",
                    margin: "1px 21px 10px 21px",
                    position: "relative",
                    height: 58,
                }}
            >
                <div
                    className="session-search-result-row-actions"
                    style={{
                        position: "absolute",
                        left: 20,
                        width: 300,
                        background:
                            "linear-gradient(to right,  rgba(255,255,255,1) 0%,rgba(255,255,255,1) 100px,rgba(255,255,255,0) 99%,rgba(255,255,255,0) 100%)",
                    }}
                >
                    <ButtonGroup large minimal>
                        <Tooltip
                            content={isPinned ? "Unpin" : "Pin"}
                            minimal
                            placement="bottom-start"
                        >
                            <Button
                                loading={updatingPin}
                                icon={faIcon({
                                    icon: isPinned
                                        ? faThumbTackSlash
                                        : faThumbTack,
                                    size: isPinned ? 20 : 16,
                                })}
                                onClick={(event) => {
                                    handlePinSession();
                                    event.stopPropagation();
                                }}
                            />
                        </Tooltip>
                        <Tooltip
                            content="Copy session ID"
                            minimal
                            placement="bottom"
                        >
                            <Button
                                onClick={(event) => {
                                    copy(sessionId);
                                    AppToaster.show({
                                        icon: faIcon({
                                            icon: faClipboard,
                                        }),
                                        message: `Copied "${sessionId}"`,
                                    });
                                    event.stopPropagation();
                                }}
                                icon={faIcon({
                                    icon: faCopy,
                                })}
                            />
                        </Tooltip>
                    </ButtonGroup>
                </div>
                <H5
                    className={`margin-0 ${Classes.TEXT_OVERFLOW_ELLIPSIS}`}
                    style={{ width: 300 }}
                >
                    #&nbsp;{sessionName}
                </H5>
                <div
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                    style={{
                        marginLeft: 10,
                        paddingRight: 235,
                    }}
                >
                    {sessionDescription}
                </div>
                <div
                    style={{
                        position: "absolute",
                        right: 20,
                    }}
                >
                    <SessionMemberStack sessionId={sessionId} size={5} />
                </div>
            </Card>
        </div>
    );
}

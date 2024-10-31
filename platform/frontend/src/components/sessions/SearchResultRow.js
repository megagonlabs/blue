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
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useRouter } from "next/router";
import { useContext } from "react";
import { AppContext } from "../contexts/app-context";
import { useSocket } from "../hooks/useSocket";
export default function SearchResultRow({ sessionId, style = {} }) {
    const { appState, appActions } = useContext(AppContext);
    const sessionDetails = _.get(
        appState,
        ["session", "sessionDetails", sessionId],
        {}
    );
    const sessionName = _.get(sessionDetails, "name", sessionId);
    const sessionDescription = _.get(sessionDetails, "description", "");
    const router = useRouter();
    const { socket } = useSocket();
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
                        left: 9,
                        width: 300,
                        background:
                            "linear-gradient(to right,  rgba(255,255,255,1) 0%,rgba(255,255,255,1) 89px,rgba(255,255,255,0) 99%,rgba(255,255,255,0) 100%)",
                    }}
                >
                    <ButtonGroup large minimal>
                        <Tooltip>
                            <Button
                                icon={faIcon({
                                    icon: faThumbTack,
                                })}
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

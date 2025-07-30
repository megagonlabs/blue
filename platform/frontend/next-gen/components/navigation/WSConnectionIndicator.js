import { useSocketStore } from "@/stores/socket-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Intent,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import { faSatelliteDish } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useShallow } from "zustand/react/shallow";
import { CIRCLE_DOT_WITH_FADE } from "../constants";
import { FAIcon } from "../FAIcon";
export default function WSConnectionIndicator() {
    const { socketReadyState, connectWebSocket, socket } = useSocketStore(
        useShallow((state) => ({
            socketReadyState: state.socketReadyState,
            connectWebSocket: state.connectWebSocket,
            socket: state.socket,
        }))
    );
    return (
        <div style={{ marginBottom: 20, textAlign: "center" }}>
            {_.isEqual(socketReadyState, WebSocket.OPEN) ? (
                CIRCLE_DOT_WITH_FADE
            ) : (
                <ButtonGroup
                    vertical
                    fill
                    size={Size.LARGE}
                    variant={ButtonVariant.MINIMAL}
                >
                    <Tooltip content="Reconnect" placement="right">
                        <Button
                            loading={_.includes(
                                [WebSocket.CONNECTING, WebSocket.CLOSING],
                                socketReadyState
                            )}
                            disabled={!_.isFunction(connectWebSocket)}
                            onClick={connectWebSocket}
                            intent={Intent.DANGER}
                            icon={<FAIcon icon={faSatelliteDish} />}
                        />
                    </Tooltip>
                </ButtonGroup>
            )}
        </div>
    );
}

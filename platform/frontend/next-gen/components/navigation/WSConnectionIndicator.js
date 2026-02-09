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
    const { socketReadyState, connectWebSocket } = useSocketStore(
        useShallow((state) => ({
            socketReadyState: state.socketReadyState,
            connectWebSocket: state.connectWebSocket,
        }))
    );
    const loading = _.includes(
        [WebSocket.CONNECTING, WebSocket.CLOSING],
        socketReadyState
    );
    return (
        <div style={{ marginBottom: 20, textAlign: "center" }}>
            {_.isEqual(socketReadyState, WebSocket.OPEN) ? (
                <Button
                    className="pointer-events-none"
                    variant={ButtonVariant.MINIMAL}
                    icon={CIRCLE_DOT_WITH_FADE}
                />
            ) : (
                <ButtonGroup
                    vertical
                    fill
                    size={Size.LARGE}
                    variant={ButtonVariant.MINIMAL}
                >
                    <Tooltip
                        content={`Reconnect${loading ? "ing" : null}`}
                        placement="right"
                    >
                        <Button
                            loading={loading}
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

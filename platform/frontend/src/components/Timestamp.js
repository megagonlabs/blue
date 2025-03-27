import { Tooltip } from "@blueprintjs/core";
import ReactTimeAgo from "react-time-ago";
export default function Timestamp({ timestamp, placement = "bottom" }) {
    return (
        <Tooltip
            minimal
            placement={placement}
            content={
                <>
                    {new Date(timestamp).toLocaleDateString()}&nbsp;at&nbsp;
                    {new Date(timestamp).toLocaleTimeString()}
                </>
            }
        >
            <ReactTimeAgo
                tooltip={false}
                date={new Date(timestamp)}
                locale="en-US"
            />
        </Tooltip>
    );
}

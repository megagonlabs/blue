import { Tooltip } from "@blueprintjs/core";
import ReactTimeAgo from "react-time-ago";
export default function Timestamp({
    epoch,
    placement = null,
    boundary = null,
}) {
    return (
        <Tooltip
            boundary={boundary}
            placement={placement}
            content={
                <>
                    {new Date(epoch).toLocaleDateString()} at&nbsp;
                    {new Date(epoch).toLocaleTimeString()}
                </>
            }
        >
            <ReactTimeAgo tooltip={false} date={new Date(epoch)} />
        </Tooltip>
    );
}

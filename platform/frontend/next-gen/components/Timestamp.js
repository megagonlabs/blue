import { Tooltip } from "@blueprintjs/core";
import ReactTimeAgo from "react-time-ago";
export default function Timestamp({ date, placement = null, boundary = null }) {
    return (
        <Tooltip
            boundary={boundary}
            placement={placement}
            content={
                <>
                    {new Date(date).toLocaleDateString()} at&nbsp;
                    {new Date(date).toLocaleTimeString()}
                </>
            }
        >
            <ReactTimeAgo tooltip={false} date={new Date(date)} />
        </Tooltip>
    );
}

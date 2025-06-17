import { faEllipsis } from "@fortawesome/sharp-duotone-solid-svg-icons";
import JsonView from "react18-json-view";
import "react18-json-view/src/style.css";
import { FAIcon } from "./FAIcon";
export default function JSONViewer({
    json,
    enableClipboard,
    collapsed = false,
}) {
    return (
        <JsonView
            collapsed={collapsed}
            customizeCollapseStringUI={() => (
                <>&nbsp;{<FAIcon icon={faEllipsis} />}</>
            )}
            displaySize
            enableClipboard={enableClipboard}
            src={json}
        />
    );
}

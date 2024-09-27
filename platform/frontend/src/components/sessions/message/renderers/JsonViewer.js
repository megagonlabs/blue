import { faIcon } from "@/components/icon";
import { faEllipsis } from "@fortawesome/pro-duotone-svg-icons";
import JsonView from "react18-json-view";
import "react18-json-view/src/style.css";
export default function JsonViewer({ json, displaySize, enableClipboard }) {
    return (
        <JsonView
            customizeCollapseStringUI={() => (
                <>&nbsp;{faIcon({ icon: faEllipsis })}</>
            )}
            displaySize={displaySize}
            enableClipboard={enableClipboard}
            src={json}
        />
    );
}

import { faIcon } from "@/components/icon";
import { faEllipsis } from "@fortawesome/sharp-duotone-solid-svg-icons";
import JsonView from "react18-json-view";
import "react18-json-view/src/style.css";
export default function JsonViewer({ json, enableClipboard }) {
    return (
        <JsonView
            customizeCollapseStringUI={() => (
                <>&nbsp;{faIcon({ icon: faEllipsis })}</>
            )}
            displaySize
            enableClipboard={enableClipboard}
            src={json}
        />
    );
}

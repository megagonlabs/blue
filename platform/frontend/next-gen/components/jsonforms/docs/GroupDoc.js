import { FAIcon } from "@/components/FAIcon";
import JSONViewer from "@/components/JSONViewer";
import * as docProps from "@/components/jsonforms/docs/constant";
import { EntityTitle, H1, H2, HTMLTable, Pre } from "@blueprintjs/core";
import { faObjectGroup } from "@fortawesome/sharp-duotone-solid-svg-icons";
import CopyDocJSONButton from "./CopyDocJSONButton";
const docJson = {
    type: "Group",
    label: "",
    props: { style: {} },
    elements: [],
};
export default function GroupDoc() {
    return (
        <div>
            <div style={{ marginBottom: 20 }}>
                <EntityTitle
                    title="Group"
                    heading={H1}
                    icon={<FAIcon icon={faObjectGroup} size={30} />}
                />
            </div>
            <Pre style={{ position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", right: 15, top: 13 }}>
                    <CopyDocJSONButton
                        docJson={JSON.stringify(docJson, null, 4)}
                        copyMessage="Copied Group JSON"
                    />
                </div>
                <JSONViewer json={docJson} enableClipboard={false} />
            </Pre>
            <H2>Props</H2>
            <HTMLTable className="docs-prop-table" style={{ width: "100%" }}>
                <thead>
                    <tr>
                        <th>Props</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>{docProps.style}</tbody>
            </HTMLTable>
        </div>
    );
}

import { FAIcon } from "@/components/FAIcon";
import JSONViewer from "@/components/JSONViewer";
import * as docProps from "@/components/jsonforms/docs/constant";
import {
    Classes,
    Code,
    EntityTitle,
    H1,
    H2,
    HTMLTable,
    Pre,
} from "@blueprintjs/core";
import { faObjectGroup } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import CopyDocJSONButton from "./CopyDocJSONButton";
const docJson = {
    type: "Group",
    label: "",
    props: {
        collapsible: false,
        defaultIsOpen: true,
        compact: false,
        style: {},
    },
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
                <tbody>
                    <tr>
                        <td>
                            <Code>collapsible</Code>
                        </td>
                        <td>
                            <strong>boolean</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                false
                            </em>
                            <div>
                                Whether this section&apos;s contents should be
                                collapsible.
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <Code>defaultIsOpen</Code>
                        </td>
                        <td>
                            <strong>boolean</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                true
                            </em>
                            <div>
                                defaultIsOpen attribute sets the default open
                                state of the group.
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <Code>compact</Code>
                        </td>
                        <td>
                            <strong>boolean</strong>
                            <em
                                className={classNames(
                                    Classes.TEXT_MUTED,
                                    "docs-prop-default"
                                )}
                            >
                                false
                            </em>
                            <div>
                                Whether this section should use compact styles.
                            </div>
                        </td>
                    </tr>
                    {docProps.style}
                </tbody>
            </HTMLTable>
        </div>
    );
}

import { convertCss } from "@/components/helper";
import { rankWith, uiTypeIs } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
import MermaidDiagram from "../MermaidDiagram";
const MermaidRenderer = ({ uischema, data }) => {
    const style = convertCss(_.get(uischema, "props.style", {}));
    return (
        <div style={{ ...style, overflow: "auto", padding: 1 }}>
            <MermaidDiagram>{data}</MermaidDiagram>
        </div>
    );
};
export default withJsonFormsControlProps(MermaidRenderer);
export const MermaidTester = rankWith(3, uiTypeIs("Mermaid"));

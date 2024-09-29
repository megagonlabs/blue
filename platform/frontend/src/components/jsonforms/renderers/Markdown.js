import { rankWith, uiTypeIs } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
const {
    default: Markdown,
} = require("@/components/sessions/message/renderers/Markdown");
const MarkdownRenderer = ({ schema, uischema }) => {
    const content = _.get(schema, "md-content", "");
    const style = _.get(uischema, "props.style", {});
    return (
        <div style={{ ...style, overflow: "auto", padding: 1 }}>
            <Markdown content={content} />
        </div>
    );
};
export default withJsonFormsControlProps(MarkdownRenderer);
export const MarkdownTester = rankWith(3, uiTypeIs("Markdown"));

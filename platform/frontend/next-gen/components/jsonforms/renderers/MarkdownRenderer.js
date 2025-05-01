import Markdown from "@/components/sessions/messages/renderers/Markdown";
import { rankWith, uiTypeIs } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
const MarkdownRenderer = ({ uischema, data }) => {
    const style = _.get(uischema, "props.style", {});
    return (
        <div style={{ ...style, overflow: "auto" }}>
            <Markdown content={data} />
        </div>
    );
};
export default withJsonFormsControlProps(MarkdownRenderer);
export const MarkdownTester = rankWith(3, uiTypeIs("Markdown"));

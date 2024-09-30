import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
export default function Markdown({ content }) {
    return (
        <ReactMarkdown
            className="react-markdown-content"
            remarkPlugins={[remarkGfm]}
        >
            {content || ""}
        </ReactMarkdown>
    );
}

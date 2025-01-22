import ReactMarkdown from "react-markdown";
import rehypeExternalLinks from "rehype-external-links";
import remarkGfm from "remark-gfm";
export default function Markdown({ content }) {
    return (
        <ReactMarkdown
            className="react-markdown-content"
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[
                [
                    rehypeExternalLinks,
                    { target: "_blank", rel: "noopener noreferrer" },
                ],
            ]}
        >
            {content || ""}
        </ReactMarkdown>
    );
}

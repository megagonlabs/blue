import ReactMarkdown from "react-markdown";
import rehypeExternalLinks from "rehype-external-links";
import rehypeRaw from "rehype-raw";
import rehypeSanitize, { defaultSchema } from "rehype-sanitize";
import remarkGfm from "remark-gfm";
import rehypeMinifyDetailsWhitespace from "./rehypeMinifyDetailsWhitespace";
export default function Markdown({ content }) {
    return (
        <div className="react-markdown-content">
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[
                    rehypeRaw,
                    rehypeMinifyDetailsWhitespace,
                    [
                        rehypeExternalLinks,
                        { target: "_blank", rel: "noopener noreferrer" },
                    ],
                    [rehypeSanitize, { schema: defaultSchema }],
                ]}
            >
                {content || ""}
            </ReactMarkdown>
        </div>
    );
}

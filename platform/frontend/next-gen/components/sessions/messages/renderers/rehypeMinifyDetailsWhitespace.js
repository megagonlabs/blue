import { isElement } from "hast-util-is-element";
import _ from "lodash";
import { visit } from "unist-util-visit";
export default function rehypeMinifyDetailsWhitespace() {
    return (tree) => {
        visit(tree, "element", (node) => {
            if (isElement(node, ["details", "summary"])) {
                node.children = node.children
                    .map((child) => {
                        if (_.isEqual(child.type, "text")) {
                            return { ...child, value: child.value.trim() };
                        }
                        return child;
                    })
                    .filter((child) => {
                        return child.type !== "text" || child.value.length > 0;
                    });
            }
        });
    };
}

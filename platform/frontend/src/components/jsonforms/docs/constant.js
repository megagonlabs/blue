const { Code, Classes } = require("@blueprintjs/core");
import classNames from "classnames";
module.exports = {
    style: (
        <tr>
            <td>
                <Code>style</Code>
            </td>
            <td>
                <strong>HTML CSS</strong>
                <em
                    className={classNames(
                        Classes.TEXT_MUTED,
                        "docs-prop-default"
                    )}
                >
                    &#123;&#125;
                </em>
                <div>Used to format the layout of this component.</div>
            </td>
        </tr>
    ),
    nameId: (
        <tr>
            <td>
                <Code>nameId</Code>
            </td>
            <td>
                <strong>string</strong>
                <em
                    className={classNames(
                        Classes.TEXT_MUTED,
                        "docs-prop-default"
                    )}
                >
                    null
                </em>
                <div>Name of the container.</div>
            </td>
        </tr>
    ),
    inline: (
        <tr>
            <td>
                <Code>inline</Code>
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
                    Whether to render the label and control on a single line.
                </div>
            </td>
        </tr>
    ),
    helperText: (
        <tr>
            <td>
                <Code>helperText</Code>
            </td>
            <td>
                <strong>string</strong>
                <em
                    className={classNames(
                        Classes.TEXT_MUTED,
                        "docs-prop-default"
                    )}
                >
                    null
                </em>
                <div>Optional helper text.</div>
            </td>
        </tr>
    ),
};

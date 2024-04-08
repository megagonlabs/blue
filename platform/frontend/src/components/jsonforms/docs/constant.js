const { Code, Classes, Callout, Intent } = require("@blueprintjs/core");
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
    numericInputTip: (
        <Callout
            title="Extended interactions"
            intent={Intent.PRIMARY}
            icon={null}
        >
            <ul>
                <li>
                    Number abbreviations: (e.g. <Code>2.1k</Code>,&nbsp;
                    <Code>-0.3m</Code>)
                </li>
                <li>
                    Scientific notation: (e.g. <Code>2.1e3</Code>,&nbsp;
                    <Code>-0.3e6</Code>)
                </li>
                <li>
                    Addition and subtraction expressions: (e.g. <Code>3+2</Code>
                    ,&nbsp;<Code>0.1m - 5k + 1</Code>)
                </li>
            </ul>
            These special-case inputs are evaluated when <Code>Enter</Code> is
            pressed (via a custom <Code>onKeyDown</Code> callback) and when the
            field loses focus (via a custom <Code>onBlur</Code> callback). If
            the input is invalid when either of these callbacks is trigged, the
            field will be cleared.
        </Callout>
    ),
};

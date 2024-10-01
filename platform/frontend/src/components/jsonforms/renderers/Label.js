import { convertCss } from "@/components/helper";
import { Classes } from "@blueprintjs/core";
import { rankWith, uiTypeIs } from "@jsonforms/core";
import { withJsonFormsCellProps } from "@jsonforms/react";
import classNames from "classnames";
import _ from "lodash";
const LabelRenderer = ({ uischema }) => {
    return (
        <div
            style={convertCss(_.get(uischema, "props.style", {}))}
            className={classNames({
                [Classes.TEXT_MUTED]: _.get(uischema, "props.muted", false),
                [Classes.TEXT_SMALL]: _.get(uischema, "props.small", false),
                [Classes.TEXT_LARGE]: _.get(uischema, "props.large", false),
            })}
        >
            {_.get(uischema, "label", null)}
        </div>
    );
};
export default withJsonFormsCellProps(LabelRenderer);
export const LabelTester = rankWith(3, uiTypeIs("Label"));

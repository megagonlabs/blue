import { Classes } from "@blueprintjs/core";
import { rankWith, uiTypeIs } from "@jsonforms/core";
import { withJsonFormsCellProps } from "@jsonforms/react";
import classNames from "classnames";
import _ from "lodash";
const LabelRenderer = ({ uischema }) => {
    const isMuted = _.get(uischema, "props.muted", false);
    const isSmall = _.get(uischema, "props.small", false);
    return (
        <div
            style={_.get(uischema, "props.style", {})}
            className={classNames({
                [Classes.TEXT_MUTED]: isMuted,
                [Classes.TEXT_SMALL]: isSmall,
            })}
        >
            {_.get(uischema, "text", null)}
        </div>
    );
};
export default withJsonFormsCellProps(LabelRenderer);
export const LabelTester = rankWith(3, uiTypeIs("Label"));

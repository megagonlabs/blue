import { convertCss } from "@/components/helper";
import { Callout } from "@blueprintjs/core";
import { rankWith, uiTypeIs } from "@jsonforms/core";
import { withJsonFormsCellProps } from "@jsonforms/react";
import _ from "lodash";
const CalloutRenderer = ({ uischema }) => {
    const label = _.get(uischema, "label", null);
    const helperText = _.get(uischema, "props.helperText", null);
    const intent = _.get(uischema, "props.intent", null);
    const style = convertCss(_.get(uischema, "props.style", null));
    return (
        <Callout style={style} intent={intent} icon={null} title={label}>
            {helperText}
        </Callout>
    );
};
export default withJsonFormsCellProps(CalloutRenderer);
export const CalloutTester = rankWith(3, uiTypeIs("Callout"));

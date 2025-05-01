import { rankWith, uiTypeIs } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
import { VegaLite } from "react-vega";
const VegaRenderer = ({ uischema, data }) => {
    const style = _.get(uischema, "props.style", {});
    return (
        <div style={{ ...style, overflow: "auto", padding: 1 }}>
            <VegaLite spec={data} actions={false} />
        </div>
    );
};
export default withJsonFormsControlProps(VegaRenderer);
export const VegaTester = rankWith(3, uiTypeIs("Vega"));

import { isDateControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
const DateRenderer = (props) => {
    console.log(props);
    return <div>date: not implemented</div>;
};
export default withJsonFormsControlProps(DateRenderer);
export const DateTester = rankWith(3, isDateControl);

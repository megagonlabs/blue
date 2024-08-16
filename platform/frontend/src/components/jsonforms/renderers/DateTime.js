import { isDateTimeControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
const DateTimeRenderer = (props) => {
    return <div>date-time: not implemented</div>;
};
export default withJsonFormsControlProps(DateTimeRenderer);
export const DateTimeTester = rankWith(3, isDateTimeControl);

import { isDateTimeControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
const DateTimeRenderer = () => {
    return <div>datetime: not implemented</div>;
};
export default withJsonFormsControlProps(DateTimeRenderer);
export const DateTimeTester = rankWith(3, isDateTimeControl);

import { isNumberControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import FormCell from "../FormCell";
import NumberInput from "../NumberInput";
const NumberRenderer = ({ uischema, handleChange, path, data, required }) => {
    const label = _.get(uischema, "label", null);
    const labelElement =
        !_.isString(label) && !required ? null : (
            <label
                style={{ fontWeight: 600 }}
                className={required ? "required" : null}
            >
                {label}
            </label>
        );
    return (
        <FormCell
            inline={_.get(uischema, "props.inline", false)}
            style={_.get(uischema, "props.style", {})}
            label={labelElement}
            helperText={_.get(uischema, "props.helperText", null)}
        >
            <NumberInput
                uischema={uischema}
                handleChange={handleChange}
                path={path}
                data={data}
            />
        </FormCell>
    );
};
export default withJsonFormsControlProps(NumberRenderer);
export const NumberTester = rankWith(3, isNumberControl);

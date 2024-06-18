import FormCell from "@/components/jsonforms/FormCell";
import NumberInput from "@/components/jsonforms/NumberInput";
import { isIntegerControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
const IntegerRenderer = ({ uischema, handleChange, path, data, required }) => {
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
                precision={0}
                handleChange={handleChange}
                path={path}
                data={data}
            />
        </FormCell>
    );
};
export default withJsonFormsControlProps(IntegerRenderer);
export const IntegerTester = rankWith(3, isIntegerControl);

import { isIntegerControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import FormCell from "../FormCell";
import NumberInput from "../NumberInput";
const IntegerRenderer = ({ uischema, handleChange, path, data, required }) => {
    const isInline = _.get(uischema, "props.inline", false);
    const label = _.get(uischema, "label", null);
    const style = _.get(uischema, "props.style", {});
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
            inline={isInline}
            style={style}
            label={labelElement}
            helperText={_.get(uischema, "props.helperText", null)}
        >
            <NumberInput
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

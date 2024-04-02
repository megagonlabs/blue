import { HTMLSelect } from "@blueprintjs/core";
import { isEnumControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
import FormCell from "../FormCell";
const EnumRenderer = ({
    uischema,
    schema,
    handleChange,
    path,
    required,
    data,
}) => {
    const enums = _.get(schema, "enum", []);
    const style = _.get(uischema, "props.style", {});
    const isInline = _.get(uischema, "props.inline", false);
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
            inline={isInline}
            style={style}
            label={labelElement}
            labelInfo={required ? "(required)" : null}
            helperText={_.get(uischema, "props.helperText", null)}
        >
            <HTMLSelect
                value={data}
                options={[
                    {
                        label: "-",
                        value: null,
                        disabled: required,
                        selected: true,
                    },
                    ...enums.map((value) => ({ label: value, value: value })),
                ]}
                onChange={(event) => {
                    let value = event.target.value;
                    if (_.isEqual(value, "-")) {
                        value = null;
                    }
                    handleChange(path, value);
                }}
            />
        </FormCell>
    );
};
export default withJsonFormsControlProps(EnumRenderer);
export const EnumTester = rankWith(3, isEnumControl);

import { InputGroup, TextArea } from "@blueprintjs/core";
import { isStringControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
import FormCell from "../FormCell";
const StringRenderer = ({ uischema, handleChange, path, data, required }) => {
    const multiline = _.get(uischema, "options.multi", false);
    const label = _.get(uischema, "label", null);
    const labelElement = _.isString(label) ? (
        <label
            style={{ fontWeight: 600 }}
            className={required ? "required" : null}
        >
            {label}
        </label>
    ) : null;
    if (multiline) {
        return (
            <FormCell inline label={labelElement}>
                <TextArea
                    value={data}
                    onChange={(event) => {
                        handleChange(path, event.target.value);
                    }}
                    fill
                    autoResize
                    style={{ resize: "vertical", minHeight: 56 }}
                />
            </FormCell>
        );
    }
    return (
        <FormCell label={labelElement}>
            <InputGroup
                large
                value={data}
                onChange={(event) => {
                    handleChange(path, event.target.value);
                }}
                fill
            />
        </FormCell>
    );
};
export default withJsonFormsControlProps(StringRenderer);
export const StringTester = rankWith(3, isStringControl);

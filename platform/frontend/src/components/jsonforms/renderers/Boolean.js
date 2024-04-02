import { Checkbox, Switch } from "@blueprintjs/core";
import { isBooleanControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
const BooleanRenderer = ({ uischema, handleChange, path, data, required }) => {
    const isSwitch = _.get(uischema, "props.switch", false);
    const style = _.get(uischema, "props.style", {});
    const label = _.get(uischema, "label", null);
    const labelElement = _.isString(label) ? (
        <label className={required ? "required" : null}>{label}</label>
    ) : null;
    const streamId = _.get(uischema, "props.streamId", null);
    const nameId = _.get(uischema, "props.nameId", null);
    const handleOnChange = (event) => {
        console.log(streamId, nameId);
        handleChange(path, event.target.checked);
    };
    if (isSwitch) {
        return (
            <Switch
                checked={data}
                label={labelElement}
                large
                onChange={handleOnChange}
            />
        );
    }
    return (
        <Checkbox
            checked={data}
            label={labelElement}
            style={style}
            large
            onChange={handleOnChange}
        />
    );
};
export default withJsonFormsControlProps(BooleanRenderer);
export const BooleanTester = rankWith(3, isBooleanControl);

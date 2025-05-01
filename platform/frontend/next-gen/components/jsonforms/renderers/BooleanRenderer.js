import { convertCss } from "@/components/helper";
import { Checkbox, Size, Switch } from "@blueprintjs/core";
import { isBooleanControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
const BooleanRenderer = ({
    uischema,
    handleChange,
    path,
    data,
    required,
    id,
}) => {
    const style = convertCss(_.get(uischema, "props.style", {}));
    const label = _.get(uischema, "label", null);
    const large = _.get(uischema, "props.large", false);
    const labelElement = _.isString(label) ? (
        <label className={required ? "required" : null}>{label}</label>
    ) : null;
    const handleOnChange = (event) => {
        handleChange(path, event.target.checked);
    };
    if (_.get(uischema, "props.switch", false)) {
        return (
            <Switch
                checked={data}
                label={labelElement}
                style={style}
                size={large ? Size.LARGE : null}
                onChange={handleOnChange}
            />
        );
    }
    return (
        <Checkbox
            name={id}
            checked={data}
            label={labelElement}
            style={style}
            size={large ? Size.LARGE : null}
            onChange={handleOnChange}
        />
    );
};
export default withJsonFormsControlProps(BooleanRenderer);
export const BooleanTester = rankWith(3, isBooleanControl);

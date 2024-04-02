import { AppContext } from "@/components/app-context";
import { Checkbox, Switch } from "@blueprintjs/core";
import { isBooleanControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
import { useContext } from "react";
const BooleanRenderer = ({ uischema, handleChange, path, data, required }) => {
    const { appState } = useContext(AppContext);
    const style = _.get(uischema, "props.style", {});
    const label = _.get(uischema, "label", null);
    const labelElement = _.isString(label) ? (
        <label className={required ? "required" : null}>{label}</label>
    ) : null;
    const handleOnChange = (event) => {
        handleChange(path, event.target.checked);
        if (_.isNil(appState.session.connection)) return;
        setTimeout(() => {
            appState.session.connection.send(
                JSON.stringify({
                    type: "INTERACTIVE_EVENT_MESSAGE",
                    stream_id: _.get(uischema, "props.streamId", null),
                    name_id: _.get(uischema, "props.nameId", null),
                    message: event.target.checked,
                    timestamp: Date.now(),
                })
            );
        }, 0);
    };
    if (_.get(uischema, "props.switch", false)) {
        return (
            <Switch
                checked={data}
                label={labelElement}
                style={style}
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

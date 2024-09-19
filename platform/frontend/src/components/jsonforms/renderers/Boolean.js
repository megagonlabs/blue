import { convertCss, sendSocketMessage } from "@/components/helper";
import { useSocket } from "@/components/hooks/useSocket";
import { Checkbox, Switch } from "@blueprintjs/core";
import { isBooleanControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
const BooleanRenderer = ({ uischema, handleChange, path, data, required }) => {
    const { socket } = useSocket();
    const style = convertCss(_.get(uischema, "props.style", {}));
    const label = _.get(uischema, "label", null);
    const labelElement = _.isString(label) ? (
        <label className={required ? "required" : null}>{label}</label>
    ) : null;
    const handleOnChange = (event) => {
        handleChange(path, event.target.checked);
        if (!_.isEqual(socket.readyState, WebSocket.OPEN)) return;
        setTimeout(() => {
            sendSocketMessage(
                socket,
                JSON.stringify({
                    type: "INTERACTIVE_EVENT_MESSAGE",
                    stream_id: _.get(uischema, "props.streamId", null),
                    path: path,
                    form_id: _.get(uischema, "props.formId", null),
                    value: event.target.checked,
                    timestamp: performance.timeOrigin + performance.now(),
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

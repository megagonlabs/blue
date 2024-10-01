import { convertCss, sendSocketMessage } from "@/components/helper";
import { useSocket } from "@/components/hooks/useSocket";
import FormCell from "@/components/jsonforms/FormCell";
import { InputGroup, TextArea } from "@blueprintjs/core";
import { isStringControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
const StringRenderer = ({
    uischema,
    handleChange,
    path,
    data,
    required,
    id,
}) => {
    const { socket } = useSocket();
    const multiline = _.get(uischema, "options.multi", false);
    const placeholder = _.get(uischema, "props.placeholder", null);
    const label = _.get(uischema, "label", null);
    const labelElement = _.isString(label) ? (
        <label
            style={{ fontWeight: 600 }}
            className={required ? "required" : null}
        >
            {label}
        </label>
    ) : null;
    const handleOnChange = (event) => {
        handleChange(path, event.target.value);
        if (!_.isEqual(socket.readyState, WebSocket.OPEN)) return;
        setTimeout(() => {
            sendSocketMessage(
                socket,
                JSON.stringify({
                    type: "INTERACTIVE_EVENT_MESSAGE",
                    stream_id: _.get(uischema, "props.streamId", null),
                    path: path,
                    form_id: _.get(uischema, "props.formId", null),
                    value: event.target.value,
                    timestamp: performance.timeOrigin + performance.now(),
                })
            );
        }, 0);
    };
    if (multiline) {
        return (
            <FormCell
                inline={_.get(uischema, "props.inline", false)}
                label={labelElement}
                style={convertCss(_.get(uischema, "props.style", {}))}
                helperText={_.get(uischema, "props.helperText", null)}
            >
                <TextArea
                    name={id}
                    placeholder={placeholder}
                    value={_.isEmpty(data) ? "" : data}
                    onChange={handleOnChange}
                    fill
                    autoResize
                    style={{ resize: "vertical", minHeight: 56 }}
                />
            </FormCell>
        );
    }
    return (
        <FormCell
            inline={_.get(uischema, "props.inline", false)}
            label={labelElement}
            style={convertCss(_.get(uischema, "props.style", {}))}
            helperText={_.get(uischema, "props.helperText", null)}
        >
            <InputGroup
                name={id}
                placeholder={placeholder}
                large
                value={_.isEmpty(data) ? "" : data}
                onChange={handleOnChange}
                fill
            />
        </FormCell>
    );
};
export default withJsonFormsControlProps(StringRenderer);
export const StringTester = rankWith(3, isStringControl);

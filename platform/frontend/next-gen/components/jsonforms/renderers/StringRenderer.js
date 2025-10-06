import { convertCss } from "@/components/helper";
import FormCell from "@/components/jsonforms/FormCell";
import { useSocketStore } from "@/stores/socket-store";
import { InputGroup, Size, TextArea } from "@blueprintjs/core";
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
    const sendMessage = useSocketStore((state) => state.sendMessage);
    const handleOnChange = (event) => {
        handleChange(path, event.target.value);
        setTimeout(() => {
            sendMessage(
                JSON.stringify({
                    type: "INTERACTIVE_EVENT_MESSAGE",
                    stream_id: _.get(uischema, "props.streamId", null),
                    path,
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
                size={Size.LARGE}
                value={_.isEmpty(data) ? "" : data}
                onChange={handleOnChange}
                fill
            />
        </FormCell>
    );
};
export default withJsonFormsControlProps(StringRenderer);
export const StringTester = rankWith(3, isStringControl);

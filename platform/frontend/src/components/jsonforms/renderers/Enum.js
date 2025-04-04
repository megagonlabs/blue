import { convertCss, sendSocketMessage } from "@/components/helper";
import { useSocket } from "@/components/hooks/useSocket";
import FormCell from "@/components/jsonforms/FormCell";
import { HTMLSelect } from "@blueprintjs/core";
import { isEnumControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
const EnumRenderer = ({
    uischema,
    schema,
    handleChange,
    path,
    required,
    data,
    id,
}) => {
    const { socket } = useSocket();
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
            style={convertCss(_.get(uischema, "props.style", {}))}
            label={labelElement}
            labelInfo={required ? "(required)" : null}
            helperText={_.get(uischema, "props.helperText", null)}
        >
            <HTMLSelect
                large={_.get(uischema, "props.large", false)}
                name={id}
                value={_.isEmpty(data) ? "" : data}
                options={[
                    {
                        label: "-",
                        value: "",
                        disabled: required,
                    },
                    ..._.get(schema, "enum", []).map((value) => ({
                        label: value,
                        value: value,
                    })),
                ]}
                onChange={(event) => {
                    let value = event.target.value;
                    if (_.isEqual(value, "")) {
                        value = null;
                    }
                    handleChange(path, value);
                    if (!_.isEqual(socket.readyState, WebSocket.OPEN)) return;
                    setTimeout(() => {
                        sendSocketMessage(
                            socket,
                            JSON.stringify({
                                type: "INTERACTIVE_EVENT_MESSAGE",
                                stream_id: _.get(
                                    uischema,
                                    "props.streamId",
                                    null
                                ),
                                path: path,
                                form_id: _.get(uischema, "props.formId", null),
                                value: value,
                                timestamp:
                                    performance.timeOrigin + performance.now(),
                            })
                        );
                    }, 0);
                }}
            />
        </FormCell>
    );
};
export default withJsonFormsControlProps(EnumRenderer);
export const EnumTester = rankWith(3, isEnumControl);

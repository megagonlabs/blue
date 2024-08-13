import { convertCss } from "@/components/helper";
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
}) => {
    const { socket } = useSocket();
    const socketReadyState = _.get(socket, "readyState", 3);
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
                value={_.isEmpty(data) ? "-" : data}
                options={[
                    {
                        label: "-",
                        value: "-",
                        disabled: required,
                        selected: true,
                    },
                    ..._.get(schema, "enum", []).map((value) => ({
                        label: value,
                        value: value,
                    })),
                ]}
                onChange={(event) => {
                    let value = event.target.value;
                    if (_.isEqual(value, "-")) {
                        value = null;
                    }
                    handleChange(path, value);
                    if (!_.isEqual(socketReadyState, 1)) {
                        return;
                    }
                    setTimeout(() => {
                        socket.send(
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

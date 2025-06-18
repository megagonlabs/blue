import { convertCss } from "@/components/helper";
import FormCell from "@/components/jsonforms/FormCell";
import { useSocketStore } from "@/stores/socket-store";
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
    const sendMessage = useSocketStore((state) => sendMessage);
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
                    setTimeout(() => {
                        sendMessage(
                            JSON.stringify({
                                type: "INTERACTIVE_EVENT_MESSAGE",
                                stream_id: _.get(
                                    uischema,
                                    "props.streamId",
                                    null
                                ),
                                path,
                                form_id: _.get(uischema, "props.formId", null),
                                value,
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

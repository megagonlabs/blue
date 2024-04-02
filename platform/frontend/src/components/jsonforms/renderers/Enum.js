import { AppContext } from "@/components/app-context";
import { HTMLSelect } from "@blueprintjs/core";
import { isEnumControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
import { useContext } from "react";
import FormCell from "../FormCell";
const EnumRenderer = ({
    uischema,
    schema,
    handleChange,
    path,
    required,
    data,
}) => {
    const { appState } = useContext(AppContext);
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
            style={_.get(uischema, "props.style", {})}
            label={labelElement}
            labelInfo={required ? "(required)" : null}
            helperText={_.get(uischema, "props.helperText", null)}
        >
            <HTMLSelect
                value={data}
                options={[
                    {
                        label: "-",
                        value: null,
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
                    if (_.isNil(appState.session.connection)) return;
                    setTimeout(() => {
                        appState.session.connection.send(
                            JSON.stringify({
                                type: "INTERACTIVE_EVENT_MESSAGE",
                                stream_id: _.get(
                                    uischema,
                                    "props.streamId",
                                    null
                                ),
                                name_id: _.get(uischema, "props.nameId", null),
                                message: value,
                                timestamp: Date.now(),
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

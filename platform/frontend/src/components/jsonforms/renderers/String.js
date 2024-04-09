import { AppContext } from "@/components/app-context";
import FormCell from "@/components/jsonforms/FormCell";
import { InputGroup, TextArea } from "@blueprintjs/core";
import { isStringControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
import { useContext } from "react";
const StringRenderer = ({ uischema, handleChange, path, data, required }) => {
    const { appState } = useContext(AppContext);
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
        if (_.isNil(appState.session.connection)) return;
        setTimeout(() => {
            appState.session.connection.send(
                JSON.stringify({
                    type: "INTERACTIVE_EVENT_MESSAGE",
                    stream_id: _.get(uischema, "props.streamId", null),
                    name_id: _.get(uischema, "props.nameId", null),
                    message: event.target.value,
                    timestamp: Date.now(),
                })
            );
        }, 0);
    };
    if (multiline) {
        return (
            <FormCell
                inline={_.get(uischema, "props.inline", false)}
                label={labelElement}
                style={_.get(uischema, "props.style", {})}
                helperText={_.get(uischema, "props.helperText", null)}
            >
                <TextArea
                    placeholder={placeholder}
                    value={data}
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
            style={_.get(uischema, "props.style", {})}
            helperText={_.get(uischema, "props.helperText", null)}
        >
            <InputGroup
                placeholder={placeholder}
                large
                value={data}
                onChange={handleOnChange}
                fill
            />
        </FormCell>
    );
};
export default withJsonFormsControlProps(StringRenderer);
export const StringTester = rankWith(3, isStringControl);

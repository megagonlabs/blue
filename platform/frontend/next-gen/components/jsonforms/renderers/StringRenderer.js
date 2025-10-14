import { convertCss } from "@/components/helper";
import FormCell from "@/components/jsonforms/FormCell";
import { useSocketStore } from "@/stores/socket-store";
import { InputGroup, Size, TextArea } from "@blueprintjs/core";
import { isStringControl, rankWith } from "@jsonforms/core";
import { withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
import { useCallback, useEffect, useMemo, useState } from "react";
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
    const [localValue, setLocalValue] = useState(data || "");
    const externalUpdateLogic = useCallback(
        (path, value) => {
            handleChange(path, value);
            setTimeout(() => {
                sendMessage(
                    JSON.stringify({
                        type: "INTERACTIVE_EVENT_MESSAGE",
                        stream_id: _.get(uischema, "props.streamId", null),
                        path,
                        form_id: _.get(uischema, "props.formId", null),
                        value,
                        timestamp: performance.timeOrigin + performance.now(),
                    })
                );
            }, 0);
        },
        [handleChange, sendMessage, uischema, path]
    );
    const debouncedExternalUpdate = useMemo(
        () => _.debounce(externalUpdateLogic, 300),
        [externalUpdateLogic]
    );
    const handleLocalChange = (event) => {
        const newValue = event.target.value;
        setLocalValue(newValue);
        debouncedExternalUpdate(path, newValue);
    };
    useEffect(() => {
        const externalValue = data || "";
        if (!_.isEqual(externalValue, localValue)) {
            setLocalValue(externalValue);
        }
    }, [data]);
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
                    value={localValue}
                    onChange={handleLocalChange}
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
                value={localValue}
                onChange={handleLocalChange}
                fill
            />
        </FormCell>
    );
};
export default withJsonFormsControlProps(StringRenderer);
export const StringTester = rankWith(3, isStringControl);

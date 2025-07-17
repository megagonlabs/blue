import { useGridContainerContext } from "@/components/contexts/GridContainerContext";
import { FAIcon } from "@/components/FAIcon";
import { showAxiosErrorToast } from "@/components/helper";
import { AppToaster } from "@/components/toaster";
import { useAppStore } from "@/stores/app-store";
import { usePlatformStore } from "@/stores/platform-store";
import {
    Button,
    ButtonVariant,
    Classes,
    Code,
    Colors,
    ControlGroup,
    Divider,
    EntityTitle,
    FormGroup,
    H3,
    Intent,
    NumericInput,
    Size,
    Tag,
} from "@blueprintjs/core";
import { faInboxFull } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useEffect, useState } from "react";
import { useShallow } from "zustand/react/shallow";
export default function SessionConfigurations() {
    const darkMode = useAppStore((state) => state.dark_mode);
    const { durationValue, loading, updateConfigurationValues } =
        usePlatformStore(
            useShallow((state) => ({
                durationValue: _.get(
                    state.configurations.values,
                    "session_expiration_duration",
                    3
                ),
                updateConfigurationValues: state.updateConfigurationValues,
                loading: state.configurations.loading,
            }))
        );
    const [duration, setDuration] = useState(durationValue);
    const durationNumber = _.toNumber(duration);
    const durationError =
        !_.isNumber(durationNumber) ||
        _.isNaN(durationNumber) ||
        durationNumber < 3;
    const [saving, setSaving] = useState(false);
    useEffect(() => {
        setDuration(durationValue);
    }, [durationValue]);
    const handleDurationSave = () => {
        setSaving(true);
        axios
            .put("/platform/settings/session_expiration_duration", {
                value: durationNumber,
            })
            .then(() => {
                AppToaster.show({
                    message: "Expiration duration has been updated.",
                    intent: Intent.SUCCESS,
                });
                updateConfigurationValues({
                    key: "session_expiration_duration",
                    value: duration,
                });
            })
            .catch((error) => {
                showAxiosErrorToast(error);
            })
            .finally(() => {
                setSaving(false);
            });
    };
    const { gridContainerId } = useGridContainerContext();
    return (
        <div id={`container-${gridContainerId}-section-0`}>
            <EntityTitle
                icon={<FAIcon icon={faInboxFull} size={20} />}
                heading={H3}
                title="Sessions"
            />
            <Divider style={{ margin: "10px 0px 10px 0px" }} />
            <div
                style={{
                    borderRadius: 2,
                    padding: 15,
                    backgroundColor: darkMode
                        ? Colors.DARK_GRAY2
                        : Colors.LIGHT_GRAY5,
                }}
            >
                <FormGroup
                    className="margin-0"
                    subLabel={
                        <div>
                            Calculated based on&nbsp;
                            <Code>created_date</Code> and&nbsp;
                            <Code>last_activity_date</Code>, sessions that are
                            outside of the expiration duration will be
                            automatically deleted &#40;
                            <Code>STREAM</Code>,&nbsp;
                            <Code>DATA</Code>
                            &nbsp;and <Code>METADATA</Code> will be removed from
                            each session&#41;. The default and minimum value is
                            3.
                        </div>
                    }
                    label="Expiration duration"
                >
                    <ControlGroup
                        style={{ marginTop: 10 }}
                        className={loading ? Classes.SKELETON : null}
                    >
                        <NumericInput
                            intent={durationError ? Intent.DANGER : null}
                            onChange={(event) => {
                                setDuration(event.target.value);
                            }}
                            value={duration}
                            style={{ width: 120 }}
                            size={Size.LARGE}
                            buttonPosition="none"
                            clampValueOnBlur
                            rightElement={<Tag minimal>days</Tag>}
                        />
                        <Button
                            loading={saving}
                            disabled={durationError}
                            size={Size.LARGE}
                            variant={ButtonVariant.MINIMAL}
                            intent={Intent.SUCCESS}
                            text="Save"
                            onClick={handleDurationSave}
                        />
                    </ControlGroup>
                </FormGroup>
            </div>
        </div>
    );
}

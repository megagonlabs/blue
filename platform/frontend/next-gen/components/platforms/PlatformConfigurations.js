import { useAppStore } from "@/stores/app-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Card,
    CardList,
    Classes,
    Code,
    Colors,
    ControlGroup,
    EntityTitle,
    H3,
    Intent,
    NumericInput,
    Size,
    Tag,
} from "@blueprintjs/core";
import { faInboxFull } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useState } from "react";
import { FAIcon } from "../FAIcon";
import { showAxiosErrorToast } from "../helper";
import withAutoSizer from "../hocs/withAutoSizer";
import { AppToaster } from "../toaster";
const SECTIONS = [{ icon: faInboxFull, text: "Sessions" }];
function PlatformConfigurations({ width, height }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const [loading, setLoading] = useState(false);
    const [configurations, setConfigurations] = useState({});
    const saveConfiguration = ({ key, value }) => {
        let newConfiguration = _.cloneDeep(configurations);
        _.set(newConfiguration, key, value);
        setConfigurations(newConfiguration);
    };
    const duration = _.get(configurations, "session_expiration_duration", 3);
    const durationNumber = _.toNumber(duration);
    const durationError =
        !_.isNumber(durationNumber) ||
        _.isNaN(durationNumber) ||
        durationNumber < 3;
    const [saving, setSaving] = useState(false);
    const handleDurationSave = () => {
        setSaving(true);
        axios
            .put("/platform/settings/session_expiration_duration", {
                value: duration,
            })
            .then(() => {
                AppToaster.show({
                    message: "Expiration duration has been updated.",
                    intent: Intent.SUCCESS,
                });
            })
            .catch((error) => {
                showAxiosErrorToast(error);
            })
            .finally(() => {
                setSaving(false);
            });
    };
    useState(() => {
        setLoading(true);
        axios
            .get("/platform/settings")
            .then((response) => {
                setConfigurations(_.get(response, "data.settings", {}));
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);
    return (
        <div style={{ width, height }}>
            <div className="full-parent-dimension" style={{ display: "flex" }}>
                <div
                    style={{
                        padding: 10,
                        overflowY: "auto",
                        minWidth: 142,
                    }}
                    className="border-right"
                >
                    <ButtonGroup
                        vertical
                        size={Size.LARGE}
                        alignText={Alignment.START}
                        variant={ButtonVariant.MINIMAL}
                    >
                        {SECTIONS.map((section) => (
                            <Button
                                icon={<FAIcon icon={section.icon} />}
                                text={section.text}
                            />
                        ))}
                    </ButtonGroup>
                </div>
                <div
                    className="full-parent-dimension"
                    style={{
                        backgroundColor: darkMode ? Colors.BLACK : null,
                        padding: 20,
                        overflowY: "auto",
                        overflowX: "hidden",
                    }}
                >
                    <div className="setting-container-section-1">
                        <div style={{ marginBottom: 10 }}>
                            <EntityTitle
                                icon={<FAIcon icon={faInboxFull} size={20} />}
                                heading={H3}
                                title="Sessions"
                            />
                        </div>
                        <CardList className="overflow-hidden">
                            <Card style={{ padding: 15 }}>
                                <div>
                                    Expiration duration
                                    <div
                                        style={{
                                            marginTop: 5,
                                            marginBottom: 10,
                                        }}
                                        className={classNames(
                                            Classes.TEXT_MUTED,
                                            Classes.TEXT_SMALL
                                        )}
                                    >
                                        Calculated based on&nbsp;
                                        <Code>created_date</Code>&nbsp;and&nbsp;
                                        <Code>last_activity_date</Code>,
                                        sessions that are outside of the
                                        expiration duration will be
                                        automatically deleted &#40;
                                        <Code>STREAM</Code>,&nbsp;
                                        <Code>DATA</Code>
                                        &nbsp;and&nbsp;
                                        <Code>METADATA</Code> will be removed
                                        from each session&#41;. The default and
                                        minimum value is 3.
                                    </div>
                                    <div>
                                        <ControlGroup
                                            className={
                                                loading
                                                    ? Classes.SKELETON
                                                    : null
                                            }
                                        >
                                            <NumericInput
                                                intent={
                                                    durationError
                                                        ? Intent.DANGER
                                                        : null
                                                }
                                                onChange={(event) => {
                                                    saveConfiguration({
                                                        key: "session_expiration_duration",
                                                        value: event.target
                                                            .value,
                                                    });
                                                }}
                                                value={duration}
                                                style={{ width: 120 }}
                                                size={Size.LARGE}
                                                buttonPosition="none"
                                                clampValueOnBlur
                                                rightElement={
                                                    <Tag minimal>days</Tag>
                                                }
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
                                    </div>
                                </div>
                            </Card>
                        </CardList>
                    </div>
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(PlatformConfigurations);

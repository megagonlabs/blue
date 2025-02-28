import { axiosErrorToast } from "@/components/helper";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    Classes,
    Code,
    ControlGroup,
    Intent,
    NumericInput,
    Section,
    SectionCard,
    Tag,
} from "@blueprintjs/core";
import axios from "axios";
import classNames from "classnames";
import { useState } from "react";
export default function SessionConfigs({ loading, configs, setLoading }) {
    const [sessionExpirationDuration, setSessionExpirationDuration] =
        useState(3);
    const sessionExpirationDurationNumber = _.toNumber(
        sessionExpirationDuration
    );
    const sessionExpirationDurationError =
        !_.isNumber(sessionExpirationDurationNumber) ||
        _.isNaN(sessionExpirationDurationNumber) ||
        sessionExpirationDurationNumber < 3;
    useState(() => {
        setSessionExpirationDuration(
            _.get(configs, "session_expiration_duration", 3)
        );
    }, [configs]);
    return (
        <Section compact title="Sessions">
            <SectionCard>
                <div>Expiration duration</div>
                <div
                    style={{ marginTop: 5, marginBottom: 10 }}
                    className={classNames(
                        Classes.TEXT_SMALL,
                        Classes.TEXT_MUTED
                    )}
                >
                    Calculated based on creation and last activity dates,
                    sessions that are outside of the expiration duration will be
                    automatically deleted &#40;
                    <Code>STREAM</Code>,&nbsp;
                    <Code>DATA</Code>
                    &nbsp;and&nbsp;
                    <Code>METADATA</Code> will be removed from each
                    session&#41;. The default and minimum value is 3 days.
                </div>
                <ControlGroup>
                    <NumericInput
                        intent={
                            sessionExpirationDurationError
                                ? Intent.DANGER
                                : null
                        }
                        className={loading ? Classes.SKELETON : null}
                        buttonPosition="none"
                        clampValueOnBlur
                        value={sessionExpirationDuration}
                        style={{ width: 120 }}
                        large
                        onChange={(event) => {
                            setSessionExpirationDuration(event.target.value);
                        }}
                        rightElement={<Tag minimal>days</Tag>}
                    />
                    <Button
                        large
                        minimal
                        intent={Intent.SUCCESS}
                        text="Save"
                        loading={loading}
                        disabled={sessionExpirationDurationError}
                        onClick={() => {
                            setLoading(true);
                            axios
                                .put(
                                    "/platform/settings/session_expiration_duration",
                                    { value: sessionExpirationDuration }
                                )
                                .then(() =>
                                    AppToaster.show({
                                        message:
                                            "Expiration duration has been updated",
                                        intent: Intent.SUCCESS,
                                    })
                                )
                                .catch((error) => {
                                    axiosErrorToast(error);
                                })
                                .finally(() => {
                                    setLoading(false);
                                });
                        }}
                    />
                </ControlGroup>
            </SectionCard>
        </Section>
    );
}

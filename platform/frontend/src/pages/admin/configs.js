import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    ButtonGroup,
    Card,
    Classes,
    Code,
    ControlGroup,
    H4,
    Intent,
    NumericInput,
    Section,
    SectionCard,
    Tag,
} from "@blueprintjs/core";
import { faInboxFull } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useEffect, useState } from "react";
export default function Configs() {
    const [loading, setLoading] = useState(false);
    const [sessionExpirationDuration, setSessionExpirationDuration] =
        useState(3);
    const sessionExpirationDurationNumber = _.toNumber(
        sessionExpirationDuration
    );
    const sessionExpirationDurationError =
        !_.isNumber(sessionExpirationDurationNumber) ||
        _.isNaN(sessionExpirationDurationNumber) ||
        sessionExpirationDurationNumber < 3;
    useEffect(() => {
        setLoading(true);
        axios.get("/platform/settings").then((response) => {
            setSessionExpirationDuration(
                _.get(response, "data.settings.session_expiration_duration", 3)
            );
            setLoading(false);
        });
    }, []);
    return (
        <>
            <Card
                style={{
                    padding: 5,
                    borderRadius: 0,
                    position: "relative",
                    zIndex: 1,
                    cursor: "default",
                }}
            >
                <ButtonGroup large minimal>
                    <Button
                        disabled
                        style={{ cursor: "default" }}
                        text={<H4 className="margin-0">Configs</H4>}
                    />
                </ButtonGroup>
            </Card>
            <Card
                style={{ padding: 5, position: "absolute", top: 70, left: 20 }}
            >
                <ButtonGroup vertical large minimal>
                    <Button
                        icon={faIcon({
                            icon: faInboxFull,
                            style: { marginRight: 10 },
                        })}
                        text="Sessions"
                    />
                </ButtonGroup>
            </Card>
            <div
                className="full-parent-width"
                style={{
                    overflowY: "auto",
                    height: "calc(100% - 50px)",
                    padding: "20px 20px 20px 170.55px",
                }}
            >
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
                            Calculated based on creation and last activity
                            dates, sessions that are outside of the expiration
                            duration will be automatically deleted &#40;
                            <Code>STREAM</Code>,&nbsp;
                            <Code>DATA</Code>
                            &nbsp;and&nbsp;
                            <Code>METADATA</Code> will be removed from each
                            session&#41;. The default and minimum value is 3
                            days.
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
                                    setSessionExpirationDuration(
                                        event.target.value
                                    );
                                }}
                                rightElement={<Tag minimal>days</Tag>}
                            />
                            <Button
                                large
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
                                            reject(false);
                                        })
                                        .finally(() => {
                                            setLoading(false);
                                        });
                                }}
                            />
                        </ControlGroup>
                    </SectionCard>
                </Section>
            </div>
        </>
    );
}

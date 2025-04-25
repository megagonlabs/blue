import { FAIcon } from "@/components/FAIcon";
import { settlePromises, showAxiosErrorToast } from "@/components/helper";
import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    Classes,
    Colors,
    FormGroup,
    InputGroup,
    Intent,
    ProgressBar,
    Section,
    SectionCard,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faBullseyeArrow,
    faCheck,
    faMoneySimpleFromBracket,
    faPercent,
    faStopwatch,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useEffect, useState } from "react";
import { useShallow } from "zustand/react/shallow";
export default function SessionBudget({ sessionId }) {
    const { sessions, setSessionDetails } = useSessionStore(
        useShallow((state) => ({
            sessions: state.sessions,
            setSessionDetails: state.setSessionDetails,
        }))
    );
    const details = _.get(sessions, [sessionId, "details"], {});
    const budget = _.get(details, "budget", {});
    const useCost = _.get(budget, "use.cost", -1);
    const allocationCost = _.get(budget, "allocation.cost", -1);
    const useAccuracy = _.get(budget, "use.accuracy", -1);
    const useLatency = _.get(budget, "use.latency", -1);
    const [cost, setCost] = useState("");
    const costNumber = _.toNumber(cost);
    const costError =
        !_.isNumber(costNumber) || _.isNaN(costNumber) || costNumber < 0;
    const [accuracy, setAccuracy] = useState("");
    const accuracyNumber = _.toNumber(accuracy);
    const accuracyError =
        !_.isNumber(accuracyNumber) ||
        _.isNaN(accuracyNumber) ||
        accuracyNumber < 0 ||
        accuracy > 100;
    const [latency, setLatency] = useState("");
    const latencyNumber = _.toNumber(latency);
    const latencyError =
        !_.isNumber(latencyNumber) ||
        _.isNaN(latencyNumber) ||
        latencyNumber < 0;
    const [loading, setLoading] = useState(false);
    useEffect(() => {
        const budgetCost = _.get(budget, "allocation.cost", -1);
        if (!_.isNil(budgetCost) && budgetCost >= 0) {
            setCost(_.toString(budgetCost));
        }
        const budgetAccuracy = _.get(budget, "allocation.accuracy", -1);
        if (!_.isNil(budgetAccuracy) && budgetAccuracy >= 0) {
            setAccuracy(_.toString(budgetAccuracy * 100));
        }
        const budgetLatency = _.get(budget, "allocation.latency", -1);
        if (!_.isNil(budgetLatency) && budgetAccuracy >= 0) {
            setLatency(_.toString((budgetLatency * 1000).toFixed(0)));
        }
    }, [budget]);
    useEffect(() => {
        setLoading(true);
        axios
            .get(`/sessions/session/${sessionId}/budget`)
            .then((response) => {
                setSessionDetails({
                    sessionId,
                    fields: [
                        {
                            path: "budget",
                            value: _.get(response, "data.result", {}),
                        },
                    ],
                });
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);
    const handleSave = () => {
        if (costError || accuracyError || latencyError) return;
        setLoading(true);
        let tasks = [
            new Promise((resolve, reject) => {
                const url = `/sessions/session/${sessionId}/budget/allocation/cost/${costNumber}`;
                axios
                    .post(url)
                    .then(() => {
                        resolve(true);
                    })
                    .catch((error) => {
                        showAxiosErrorToast(error);
                        reject(false);
                    });
            }),
            new Promise((resolve, reject) => {
                const url = `/sessions/session/${sessionId}/budget/allocation/accuracy/${
                    accuracyNumber / 100
                }`;
                axios
                    .post(url)
                    .then(() => {
                        resolve(true);
                    })
                    .catch((error) => {
                        axiosErrorToast(error);
                        reject(false);
                    });
            }),
            new Promise((resolve, reject) => {
                const url = `/sessions/session/${sessionId}/budget/allocation/latency/${
                    latencyNumber / 1000
                }`;
                axios
                    .post(url)
                    .then(() => {
                        resolve(true);
                    })
                    .catch((error) => {
                        axiosErrorToast(error);
                        reject(false);
                    });
            }),
        ];
        settlePromises(tasks, () => {
            setLoading(false);
            setSessionDetails({
                sessionId,
                fields: [
                    { path: "budget.allocation.cost", value: costNumber },
                    {
                        path: "budget.allocation.accuracy",
                        value: accuracyNumber / 100,
                    },
                    {
                        path: "budget.allocation.latency",
                        value: latencyNumber / 1000,
                    },
                ],
            });
        });
    };
    return (
        <div
            className="full-parent-dimension"
            style={{ padding: 20, overflowY: "auto" }}
        >
            <Section style={{ marginBottom: 15 }} compact title="Cost">
                <SectionCard>
                    <div style={{ display: "flex", gap: 15 }}>
                        <FormGroup
                            style={{ maxWidth: 200 }}
                            label="Allocation"
                            className="full-parent-width margin-0"
                        >
                            <InputGroup
                                readOnly={loading}
                                intent={costError ? Intent.DANGER : null}
                                value={cost}
                                onValueChange={(value) => setCost(value)}
                                leftIcon={
                                    <FAIcon icon={faMoneySimpleFromBracket} />
                                }
                                size={Size.LARGE}
                            />
                        </FormGroup>
                        <FormGroup
                            label="Used"
                            className="full-parent-width margin-0"
                        >
                            <div
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 5,
                                    height: 40,
                                }}
                            >
                                <div
                                    style={{ fontWeight: 600 }}
                                    className={Classes.TEXT_LARGE}
                                >
                                    {!_.isNil(useCost) && useCost >= 0
                                        ? useCost
                                        : "-"}
                                </div>
                                {!_.isNil(useCost) &&
                                    useCost >= 0 &&
                                    !_.isNil(allocationCost) &&
                                    allocationCost >= 0 && (
                                        <Tooltip
                                            placement="top"
                                            content={`${useCost} / ${allocationCost}`}
                                        >
                                            <ProgressBar
                                                style={{ width: 40 }}
                                                intent={Intent.PRIMARY}
                                                stripes={false}
                                                value={useCost / allocationCost}
                                            />
                                        </Tooltip>
                                    )}
                            </div>
                        </FormGroup>
                    </div>
                </SectionCard>
            </Section>
            <Section style={{ marginBottom: 15 }} compact title="Accuracy">
                <SectionCard>
                    <div style={{ display: "flex", gap: 15 }}>
                        <FormGroup
                            style={{ maxWidth: 200 }}
                            label="Target"
                            className="full-parent-width margin-0"
                        >
                            <InputGroup
                                readOnly={loading}
                                intent={accuracyError ? Intent.DANGER : null}
                                value={accuracy}
                                onValueChange={(value) => setAccuracy(value)}
                                rightElement={
                                    <Tag
                                        minimal
                                        icon={<FAIcon icon={faPercent} />}
                                    />
                                }
                                leftIcon={<FAIcon icon={faBullseyeArrow} />}
                                size={Size.LARGE}
                            />
                        </FormGroup>
                        <FormGroup
                            label="Worst"
                            className="full-parent-width margin-0"
                        >
                            <div
                                style={{
                                    fontWeight: 600,
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 5,
                                    height: 40,
                                    color:
                                        (useAccuracy * 100).toFixed(10) >=
                                        accuracyNumber
                                            ? Colors.GREEN3
                                            : null,
                                }}
                                className={Classes.TEXT_LARGE}
                            >
                                <div>
                                    {!_.isNil(useAccuracy) && useAccuracy >= 0
                                        ? (useAccuracy * 100).toFixed(10)
                                        : "-"}
                                </div>
                                <FAIcon
                                    icon={faPercent}
                                    className={Classes.TEXT_MUTED}
                                />
                            </div>
                        </FormGroup>
                    </div>
                </SectionCard>
            </Section>
            <Section style={{ marginBottom: 15 }} compact title="Latency">
                <SectionCard>
                    <div style={{ display: "flex", gap: 15 }}>
                        <FormGroup
                            style={{ maxWidth: 200 }}
                            label="Target"
                            className="full-parent-width margin-0"
                        >
                            <InputGroup
                                readOnly={loading}
                                intent={latencyError ? Intent.DANGER : null}
                                value={latency}
                                onValueChange={(value) => setLatency(value)}
                                rightElement={<Tag minimal>ms</Tag>}
                                leftIcon={<FAIcon icon={faStopwatch} />}
                                size={Size.LARGE}
                            />
                        </FormGroup>
                        <FormGroup
                            label="Slowest"
                            className="full-parent-width margin-0"
                        >
                            <div
                                style={{
                                    fontWeight: 600,
                                    display: "flex",
                                    gap: 5,
                                    alignItems: "center",
                                    height: 40,
                                    color:
                                        (useLatency * 1000).toFixed(0) <=
                                        latencyNumber
                                            ? Colors.GREEN3
                                            : null,
                                }}
                                className={Classes.TEXT_LARGE}
                            >
                                {!_.isNil(useLatency) && useLatency >= 0
                                    ? (useLatency * 1000).toFixed(0)
                                    : "-"}
                                <label className={Classes.TEXT_MUTED}>ms</label>
                            </div>
                        </FormGroup>
                    </div>
                </SectionCard>
            </Section>
            <Button
                loading={loading}
                disabled={costError || accuracyError || latencyError}
                icon={<FAIcon icon={faCheck} />}
                size={Size.LARGE}
                text="Save"
                onClick={handleSave}
                intent={Intent.SUCCESS}
            />
        </div>
    );
}

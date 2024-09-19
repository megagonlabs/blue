import { AppContext } from "@/components/contexts/app-context";
import { settlePromises } from "@/components/helper";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    Card,
    Classes,
    DialogBody,
    DialogFooter,
    FormGroup,
    H4,
    H5,
    Intent,
    NumericInput,
    ProgressBar,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faBullseyeArrow,
    faCheck,
    faMoneySimpleFromBracket,
    faStopwatch,
} from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
export default function SessionBudget({
    loading,
    setLoading,
    setAllowQuickClose,
}) {
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [budget, setBudget] = useState({});
    const [cost, setCost] = useState("");
    const [accuracy, setAccuracy] = useState("");
    const [latency, setLatency] = useState("");
    const costNumber = _.toNumber(cost);
    const costError =
        !_.isNumber(costNumber) || _.isNaN(costNumber) || costNumber < 0;
    const accuracyNumber = _.toNumber(accuracy);
    const accuracyError =
        !_.isNumber(accuracyNumber) ||
        _.isNaN(accuracyNumber) ||
        accuracyNumber < 0 ||
        accuracy > 100;
    const latencyNumber = _.toNumber(latency);
    const latencyError =
        !_.isNumber(latencyNumber) ||
        _.isNaN(latencyNumber) ||
        latencyNumber < 0;
    const useCost = _.get(budget, "use.cost", -1);
    const allocationCost = _.get(budget, "allocation.cost", -1);
    const useAccuracy = _.get(budget, "use.accuracy", -1);
    const useLatency = _.get(budget, "use.latency", -1);
    const fetchBudget = () => {
        setLoading(true);
        axios
            .get(`/sessions/session/${sessionIdFocus}/budget`)
            .then((response) => {
                setBudget(_.get(response, "data.result"), {});
                const responseCost = _.get(
                    response,
                    "data.result.allocation.cost",
                    -1
                );
                if (!_.isNil(responseCost) && responseCost >= 0) {
                    setCost(_.toString(responseCost));
                }
                const responseAccuracy = _.get(
                    response,
                    "data.result.allocation.accuracy",
                    -1
                );
                if (!_.isNil(responseAccuracy) && responseAccuracy >= 0) {
                    setAccuracy(_.toString(responseAccuracy));
                }
                const responseLatency = _.get(
                    response,
                    "data.result.allocation.latency",
                    -1
                );
                if (!_.isNil(responseLatency) && responseLatency >= 0) {
                    setLatency(_.toString(responseLatency * 1000));
                }
                setLoading(false);
            });
    };
    useEffect(() => {
        fetchBudget();
    }, []);
    const handleSaveBudget = () => {
        if (costError || accuracyError || latencyError) return;
        setLoading(true);
        let tasks = [
            new Promise((resolve, reject) => {
                axios
                    .post(
                        `/sessions/session/${sessionIdFocus}/budget/allocation/cost/${costNumber}`
                    )
                    .then(() => {
                        resolve(true);
                    })
                    .catch((error) => {
                        AppToaster.show({
                            intent: Intent.DANGER,
                            message: `${error.name}: ${error.message}`,
                        });
                        reject(false);
                    });
            }),
            new Promise((resolve, reject) => {
                axios
                    .post(
                        `/sessions/session/${sessionIdFocus}/budget/allocation/accuracy/${accuracyNumber}`
                    )
                    .then(() => {
                        resolve(true);
                    })
                    .catch((error) => {
                        AppToaster.show({
                            intent: Intent.DANGER,
                            message: `${error.name}: ${error.message}`,
                        });
                        reject(false);
                    });
            }),
            new Promise((resolve, reject) => {
                axios
                    .post(
                        `/sessions/session/${sessionIdFocus}/budget/allocation/latency/${
                            latencyNumber / 1000
                        }`
                    )
                    .then(() => {
                        resolve(true);
                    })
                    .catch((error) => {
                        AppToaster.show({
                            intent: Intent.DANGER,
                            message: `${error.name}: ${error.message}`,
                        });
                        reject(false);
                    });
            }),
        ];
        settlePromises(tasks, () => {
            setLoading(false);
            setAllowQuickClose(true);
            fetchBudget();
        });
    };
    return (
        <>
            <DialogBody className="dialog-body">
                <div
                    style={{
                        padding: 15,
                        display: "flex",
                        gap: 15,
                        flexWrap: "wrap",
                    }}
                >
                    <Card compact style={{ width: "calc(50% - 7.5px)" }}>
                        <H5 style={{ marginBottom: 10 }}>Cost</H5>
                        <FormGroup
                            label="Allocation"
                            style={{ marginBottom: 10 }}
                        >
                            <NumericInput
                                className={loading ? Classes.SKELETON : null}
                                intent={costError ? Intent.DANGER : null}
                                value={cost}
                                onChange={(event) => {
                                    setCost(event.target.value);
                                    setAllowQuickClose(false);
                                }}
                                leftIcon={faIcon({
                                    icon: faMoneySimpleFromBracket,
                                })}
                                large
                                fill
                                min={0}
                                buttonPosition="none"
                            />
                        </FormGroup>
                        Total
                        <H4 style={{ marginTop: 5, marginBottom: 5 }}>
                            {!_.isNil(useCost) && useCost >= 0 ? useCost : "-"}
                        </H4>
                        {!_.isNil(useCost) &&
                        useCost >= 0 &&
                        !_.isNil(allocationCost) &&
                        allocationCost >= 0 ? (
                            <Tooltip
                                placement="top"
                                className="full-parent-width"
                                content={`${useCost} / ${allocationCost}`}
                            >
                                <ProgressBar
                                    intent={Intent.PRIMARY}
                                    stripes={false}
                                    value={useCost / allocationCost}
                                />
                            </Tooltip>
                        ) : null}
                    </Card>
                    <Card compact style={{ width: "calc(50% - 7.5px)" }}>
                        <H5 style={{ marginBottom: 10 }}>Accuracy</H5>
                        <FormGroup
                            label="Allocation"
                            style={{ marginBottom: 10 }}
                        >
                            <NumericInput
                                className={loading ? Classes.SKELETON : null}
                                intent={accuracyError ? Intent.DANGER : null}
                                value={accuracy}
                                onChange={(event) => {
                                    setAccuracy(event.target.value);
                                    setAllowQuickClose(false);
                                }}
                                leftIcon={faIcon({ icon: faBullseyeArrow })}
                                large
                                fill
                                min={0}
                                max={1}
                                rightElement={<Tag minimal>%</Tag>}
                                buttonPosition="none"
                            />
                        </FormGroup>
                        Worst
                        <H4 style={{ marginTop: 5, marginBottom: 0 }}>
                            {!_.isNil(useAccuracy) && useAccuracy >= 0
                                ? (useAccuracy * 100).toFixed(10)
                                : "-"}
                            &nbsp;
                            <label className={Classes.TEXT_MUTED}>%</label>
                        </H4>
                    </Card>
                    <Card compact style={{ width: "calc(50% - 7.5px)" }}>
                        <H5 style={{ marginBottom: 10 }}>Latency</H5>
                        <FormGroup
                            label="Allocation"
                            style={{ marginBottom: 10 }}
                        >
                            <NumericInput
                                className={loading ? Classes.SKELETON : null}
                                intent={latencyError ? Intent.DANGER : null}
                                value={latency}
                                onChange={(event) => {
                                    setLatency(event.target.value);
                                    setAllowQuickClose(false);
                                }}
                                leftIcon={faIcon({ icon: faStopwatch })}
                                large
                                fill
                                min={0}
                                rightElement={<Tag minimal>ms</Tag>}
                                buttonPosition="none"
                            />
                        </FormGroup>
                        Slowest
                        <H4 style={{ marginTop: 5, marginBottom: 0 }}>
                            {!_.isNil(useLatency) && useLatency >= 0
                                ? useLatency.toFixed(10)
                                : "-"}
                            &nbsp;
                            <label className={Classes.TEXT_MUTED}>ms</label>
                        </H4>
                    </Card>
                </div>
            </DialogBody>
            <DialogFooter>
                <Button
                    disabled={costError || accuracyError || latencyError}
                    loading={loading}
                    text="Save"
                    large
                    onClick={handleSaveBudget}
                    intent={Intent.SUCCESS}
                    icon={faIcon({ icon: faCheck })}
                />
            </DialogFooter>
        </>
    );
}

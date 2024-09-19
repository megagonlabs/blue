import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { Card, FormGroup, H4, H5, NumericInput, Tag } from "@blueprintjs/core";
import {
    faBullseyeArrow,
    faMoneySimpleFromBracket,
    faStopwatch,
} from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
export default function SessionBudget() {
    const [loading, setLoading] = useState(false);
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [budget, setBudget] = useState({});
    const [cost, setCost] = useState(null);
    const [accuracy, setAccuracy] = useState(null);
    const [latency, setLatency] = useState(null);
    const useCost = _.get(budget, "use.cost", -1);
    const useAccuracy = _.get(budget, "use.accuracy", -1);
    const useLatency = _.get(budget, "use.latency", -1);
    useEffect(() => {
        axios
            .get(`/sessions/session/${sessionIdFocus}/budget`)
            .then((response) => {
                setBudget(_.get(response, "data.result"), {});
                const responseCost = _.get(
                    response,
                    "data.result.allocation.cost",
                    -1
                );
                if (!_.isEmpty(responseCost) && responseCost >= 0) {
                    setCost(responseCost);
                }
                const responseAccuracy = _.get(
                    response,
                    "data.result.allocation.accuracy",
                    -1
                );
                if (!_.isEmpty(responseAccuracy) && responseAccuracy >= 0) {
                    setAccuracy(responseAccuracy);
                }
                const responseLatency = _.get(
                    response,
                    "data.result.allocation.latency",
                    -1
                );
                if (!_.isEmpty(responseLatency) && responseLatency >= 0) {
                    setLatency(responseLatency);
                }
            });
    }, []);
    return (
        <div style={{ display: "flex", gap: 15, flexWrap: "wrap" }}>
            <Card compact style={{ width: "calc(50% - 7.5px)" }}>
                <H5 style={{ marginBottom: 10 }}>Cost</H5>
                <FormGroup label="Allocation" style={{ marginBottom: 10 }}>
                    <NumericInput
                        leftIcon={faIcon({ icon: faMoneySimpleFromBracket })}
                        large
                        fill
                        min={0}
                        buttonPosition="none"
                    />
                </FormGroup>
                Usage
                <H4>{!_.isEmpty(useCost) && useCost >= 0 ? useCost : "-"}</H4>
            </Card>
            <Card compact style={{ width: "calc(50% - 7.5px)" }}>
                <H5 style={{ marginBottom: 10 }}>Accuracy</H5>
                <FormGroup label="Allocation" style={{ marginBottom: 10 }}>
                    <NumericInput
                        leftIcon={faIcon({ icon: faBullseyeArrow })}
                        large
                        fill
                        min={0}
                        max={1}
                        rightElement={<Tag minimal>%</Tag>}
                        buttonPosition="none"
                    />
                </FormGroup>
                Usage
                <H4>
                    {!_.isEmpty(useAccuracy) && useAccuracy >= 0
                        ? useAccuracy
                        : "-"}
                </H4>
            </Card>
            <Card compact style={{ width: "calc(50% - 7.5px)" }}>
                <H5 style={{ marginBottom: 10 }}>Latency</H5>
                <FormGroup label="Allocation" style={{ marginBottom: 10 }}>
                    <NumericInput
                        leftIcon={faIcon({ icon: faStopwatch })}
                        large
                        fill
                        min={0}
                        rightElement={<Tag minimal>sec</Tag>}
                        buttonPosition="none"
                    />
                </FormGroup>
                Usage
                <H4>
                    {!_.isEmpty(useLatency) && useLatency >= 0
                        ? useLatency
                        : "-"}
                </H4>
            </Card>
        </div>
    );
}

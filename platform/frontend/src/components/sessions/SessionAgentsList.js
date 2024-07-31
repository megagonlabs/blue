import { ENTITY_ICON_40 } from "@/components/constant";
import { Card, Classes, FormGroup, NonIdealState } from "@blueprintjs/core";
import { faScreenUsers } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { AppContext } from "../contexts/app-context";
import EntityIcon from "../entity/EntityIcon";
import { faIcon } from "../icon";
export default function SessionAgentsList() {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [agents, setAgents] = useState([]);
    const [loading, setLoading] = useState(true);
    useEffect(() => {
        setLoading(true);
        axios
            .get(`/sessions/session/${sessionIdFocus}/agents`)
            .then((response) => {
                const agents = _.get(response, "data.results", []).filter(
                    (agent) => {
                        const agentTypeId = {
                            type: _.split(agent.sid, ":")[0],
                            id: _.split(agent.sid, ":")[1],
                        };
                        return !_.includes(
                            ["USER", "OBSERVER"],
                            agentTypeId.type
                        );
                    }
                );
                for (let i = 0; i < _.size(agents); i++) {
                    const agentName = agents[i].name;
                    if (!_.has(appState, ["agent", "icon", agentName])) {
                        appActions.agent.fetchIcon(agentName);
                    }
                }
                setAgents(agents);
                setLoading(false);
            });
    }, []);
    const LOADING_PLACEHOLDER = (
        <div
            style={{
                display: "flex",
                alignItems: "center",
                gap: 15,
                padding: "7.5px 15px",
                borderRadius: 2,
            }}
        >
            <Card className={Classes.SKELETON} style={ENTITY_ICON_40} />
            <div className={Classes.SKELETON} style={{ width: 163.56 }}>
                &nbsp;
            </div>
        </div>
    );
    return (
        <div style={{ minHeight: 202, height: _.isEmpty(agents) ? 202 : null }}>
            {_.isEmpty(agents) && !loading ? (
                <NonIdealState
                    className="full-parent-height"
                    icon={faIcon({ icon: faScreenUsers, size: 50 })}
                    title="No Agent"
                />
            ) : (
                <FormGroup
                    label="Currently in the session"
                    style={{ marginBottom: 0 }}
                >
                    {loading ? (
                        <>
                            {LOADING_PLACEHOLDER}
                            {LOADING_PLACEHOLDER}
                            {LOADING_PLACEHOLDER}
                        </>
                    ) : (
                        agents.map((agent, index) => {
                            const agentName = _.get(agent, "name", "-");
                            const agentSid = _.get(agent, "sid", agentName);
                            return (
                                <div
                                    key={index}
                                    className="on-hover-background-color-bp-gray-3"
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 15,
                                        padding: "7.5px 15px",
                                        borderRadius: 2,
                                    }}
                                >
                                    <Card style={ENTITY_ICON_40}>
                                        <EntityIcon
                                            entity={{
                                                type: "agent",
                                                icon: _.get(appState, [
                                                    "agent",
                                                    "icon",
                                                    agentName,
                                                ]),
                                            }}
                                        />
                                    </Card>
                                    <div style={{ fontWeight: 600 }}>
                                        {agentSid}
                                    </div>
                                </div>
                            );
                        })
                    )}
                </FormGroup>
            )}
        </div>
    );
}

import { ENTITY_ICON_40 } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import EntityIcon from "@/components/entity/EntityIcon";
import { faIcon } from "@/components/icon";
import {
    Card,
    Classes,
    DialogBody,
    FormGroup,
    NonIdealState,
} from "@blueprintjs/core";
import { faScreenUsers } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
export default function SessionAgentsList({ loading, setLoading }) {
    const { appState, appActions } = useContext(AppContext);
    const { propertyLookups } = appState.agent;
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [agents, setAgents] = useState([]);
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
                        appActions.agent.fetchAttributes(agentName);
                    }
                }
                setAgents(agents);
                setLoading(false);
            });
    }, []); // eslint-disable-line react-hooks/exhaustive-deps
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
        <DialogBody>
            <div
                style={{
                    minHeight: 202,
                    height: _.isEmpty(agents) ? 202 : null,
                    maxHeight: 463,
                }}
            >
                {_.isEmpty(agents) && !loading ? (
                    <NonIdealState
                        className="full-parent-height"
                        icon={faIcon({ icon: faScreenUsers, size: 50 })}
                        title="No Agent"
                    />
                ) : (
                    <FormGroup label="Currently in the session">
                        {loading ? (
                            <>
                                {LOADING_PLACEHOLDER}
                                {LOADING_PLACEHOLDER}
                            </>
                        ) : (
                            agents.map((agent, index) => {
                                const agentName = _.get(agent, "name", "-");
                                const agentSid = _.get(agent, "sid", agentName);
                                const displayName = _.get(
                                    propertyLookups,
                                    [agentName, "display_name"],
                                    null
                                );
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
                                        <div
                                            style={{
                                                fontWeight: 600,
                                                width: "calc(100% - 55px)",
                                            }}
                                        >
                                            {!_.isEmpty(displayName) && (
                                                <div
                                                    className={
                                                        Classes.TEXT_OVERFLOW_ELLIPSIS
                                                    }
                                                >
                                                    {displayName}
                                                </div>
                                            )}
                                            {agentSid}
                                        </div>
                                    </div>
                                );
                            })
                        )}
                    </FormGroup>
                )}
            </div>
        </DialogBody>
    );
}

import { FAIcon } from "@/components/FAIcon";
import RegistryEntityIcon from "@/components/registries/RegistryEntityIcon";
import { useAgentStore } from "@/stores/agent-store";
import { useDedupStore } from "@/stores/dedup-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Card,
    CardList,
    Classes,
    Colors,
    NonIdealState,
} from "@blueprintjs/core";
import { faScreenUsers } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useEffect, useState } from "react";
const IGNORED_AGENT_TYPES = ["USER", "OBSERVER"];
export default function SessionAgents({ sessionId }) {
    const sessions = useSessionStore((state) => state.sessions);
    const setSessionDetails = useSessionStore(
        (state) => state.setSessionDetails
    );
    const getAgentMetadata = useDedupStore((state) => state.getAgentMetadata);
    const metadata = useAgentStore((state) => state.metadata);
    const details = _.get(sessions, [sessionId, "details"], {});
    const [loading, setLoading] = useState(false);
    const [agents, setAgents] = useState(_.get(details, "agents", []));
    useEffect(() => {
        if (!_.isEqual(details.agents, agents)) {
            setAgents(details.agents);
        }
    }, [details.agents]);
    useEffect(() => {
        setLoading(true);
        axios
            .get(`/sessions/session/${sessionId}/agents`)
            .then((response) => {
                const agents = _.get(response, "data.results", []).filter(
                    (agent) => {
                        const type = _.split(agent.sid, ":")[0];
                        return !_.includes(IGNORED_AGENT_TYPES, type);
                    }
                );
                for (let i = 0; i < _.size(agents); i++) {
                    getAgentMetadata(agents[i].name);
                }
                setSessionDetails({
                    sessionId,
                    fields: [{ path: "agents", value: agents }],
                });
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);
    return (
        <div className="full-parent-dimension">
            {_.isEmpty(agents) ? (
                <NonIdealState
                    title="No Agent"
                    icon={<FAIcon icon={faScreenUsers} size={50} />}
                />
            ) : (
                <CardList bordered={false} style={{ padding: "10px 20px" }}>
                    {agents.map((agent, index) => {
                        const displayName = _.get(
                            metadata,
                            [agent.name, "displayName"],
                            agent.name
                        );
                        return (
                            <Card
                                key={index}
                                style={{ position: "relative", height: 60 }}
                            >
                                <div
                                    className="padding-0 overflow-hidden custom-card"
                                    style={{
                                        position: "absolute",
                                        left: 0,
                                        top: 10,
                                        height: 40,
                                        width: 40,
                                        display: "flex",
                                        borderRadius: 2,
                                        justifyContent: "center",
                                        alignItems: "center",
                                        backgroundColor: Colors.WHITE,
                                    }}
                                >
                                    <RegistryEntityIcon
                                        content={_.get(
                                            metadata,
                                            [agent.name, "icon"],
                                            null
                                        )}
                                    />
                                </div>
                                <div
                                    style={{
                                        height: 40,
                                        marginLeft: 30,
                                        display: "flex",
                                        flexDirection: "column",
                                        justifyContent: "space-between",
                                    }}
                                >
                                    <div>{displayName}</div>
                                    <div className={Classes.TEXT_MUTED}>
                                        {agent.sid}
                                    </div>
                                </div>
                            </Card>
                        );
                    })}
                </CardList>
            )}
        </div>
    );
}

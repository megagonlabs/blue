import { Card, Classes, FormGroup } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { AppContext } from "../contexts/app-context";
export default function SessionAgentsList() {
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [agents, setAgents] = useState([]);
    const [loading, setLoading] = useState(false);
    useEffect(() => {
        setLoading(true);
        axios
            .get(`/sessions/session/${sessionIdFocus}/agents`)
            .then((response) => {
                setLoading(false);
                setAgents(_.get(response, "data.results", []));
            });
    }, []);
    return (
        <div
            className={loading ? Classes.SKELETON : null}
            style={{ minHeight: 202 }}
        >
            <FormGroup label="In this session" style={{ marginBottom: 0 }}>
                {agents.map((agent) => (
                    <div
                        className="on-hover-background-color-bp-gray-3"
                        style={{
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            gap: 15,
                            padding: "7.5px 15px",
                            borderRadius: 2,
                        }}
                    >
                        <Card
                            style={{
                                borderRadius: "50%",
                                padding: 0,
                                overflow: "hidden",
                                width: 40,
                                height: 40,
                            }}
                        ></Card>
                        {agent}
                    </div>
                ))}
            </FormGroup>
        </div>
    );
}

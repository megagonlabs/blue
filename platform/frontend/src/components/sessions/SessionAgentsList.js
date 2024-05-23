import { Card, Classes, FormGroup } from "@blueprintjs/core";
import { faCircleA } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { AppContext } from "../contexts/app-context";
import { faIcon } from "../icon";
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
            <Card
                className={Classes.SKELETON}
                style={{
                    borderRadius: "50%",
                    padding: 0,
                    overflow: "hidden",
                    width: 40,
                    height: 40,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                }}
            />
            <div className={Classes.SKELETON} style={{ width: 163.56 }}>
                &nbsp;
            </div>
        </div>
    );
    const REPLACEMENTS = { _AT_: "@", _DOT_: "." };
    const re = new RegExp(Object.keys(REPLACEMENTS).join("|"), "g");
    return (
        <div style={{ minHeight: 202 }}>
            <FormGroup label="In this session" style={{ marginBottom: 0 }}>
                {loading ? (
                    <>
                        {LOADING_PLACEHOLDER}
                        {LOADING_PLACEHOLDER}
                        {LOADING_PLACEHOLDER}
                    </>
                ) : null}
                {agents.map((agent) => {
                    const agentName = _.get(
                        agent,
                        "sid",
                        _.get(agent, "name", "-")
                    );
                    return (
                        <div
                            className="on-hover-background-color-bp-gray-3"
                            style={{
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
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                }}
                            >
                                {faIcon({
                                    icon: faCircleA,
                                    style: { color: "#5f6b7c" },
                                })}
                            </Card>
                            <div>
                                <div style={{ fontWeight: 600 }}>
                                    {agentName.replace(
                                        re,
                                        (m) => REPLACEMENTS[m]
                                    )}
                                </div>
                                <div
                                    className={classNames(
                                        Classes.TEXT_DISABLED,
                                        Classes.TEXT_SMALL
                                    )}
                                >
                                    {agentName}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </FormGroup>
        </div>
    );
}

import { PROFILE_PICTURE_40 } from "@/components/constant";
import { Card, Classes, FormGroup, NonIdealState } from "@blueprintjs/core";
import { faCircleA, faScreenUsers } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import Image from "next/image";
import { useContext, useEffect, useState } from "react";
import { AppContext } from "../contexts/app-context";
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
                setAgents(_.get(response, "data.results", []));
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
        <div style={{ minHeight: 202, height: _.isEmpty(agents) ? 202 : null }}>
            {_.isEmpty(agents) && !loading ? (
                <NonIdealState
                    className="full-parent-height"
                    icon={faIcon({ icon: faScreenUsers, size: 50 })}
                    title="It's an empty room"
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
                            const agentName = _.get(
                                agent,
                                "sid",
                                _.get(agent, "name", "-")
                            );
                            const agentTypeId = {
                                type: _.split(agent.sid, ":")[0],
                                id: _.split(agent.sid, ":")[1],
                            };
                            const hasUserProfile = _.has(appState, [
                                "app",
                                "users",
                                agentTypeId.id,
                            ]);
                            if (
                                !hasUserProfile &&
                                _.isEqual(agentTypeId.type, "USER")
                            ) {
                                appActions.app.getUserProfileByEmail(
                                    agentTypeId.id
                                );
                            }
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
                                    {_.isEqual(agentTypeId.type, "USER") &&
                                    hasUserProfile ? (
                                        <Card
                                            style={PROFILE_PICTURE_40}
                                            className="margin-0"
                                        >
                                            <Image
                                                alt=""
                                                src={_.get(
                                                    appState,
                                                    [
                                                        "app",
                                                        "users",
                                                        agentTypeId.id,
                                                        "picture",
                                                    ],
                                                    ""
                                                )}
                                                width={40}
                                                height={40}
                                            />
                                        </Card>
                                    ) : (
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
                                    )}
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
                        })
                    )}
                </FormGroup>
            )}
        </div>
    );
}

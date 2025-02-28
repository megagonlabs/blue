import { ENTITY_ICON_40 } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import EntityIcon from "@/components/entity/EntityIcon";
import { useSocket } from "@/components/hooks/useSocket";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Alignment,
    Button,
    Card,
    Classes,
    Colors,
    H1,
    Intent,
    Tooltip,
} from "@blueprintjs/core";
import {
    faHourglassStart,
    faPen,
    faPlus,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext, useEffect, useState } from "react";
const ROW_ACTION_STYLE = { position: "absolute", right: 15 };
const agentRegistryName = process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME;
export default function LaunchScreen() {
    const { user, permissions } = useContext(AuthContext);
    const { appState, appActions } = useContext(AppContext);
    const router = useRouter();
    const name = _.get(user, "name", null);
    const [agentGroups, setAgentGroups] = useState([]);
    const [loading, setLoading] = useState(true);
    const LOADING_PLACEMENT = (
        <Card className={Classes.SKELETON} style={{ marginBottom: 20 }}>
            &nbsp;
        </Card>
    );
    useEffect(() => {
        setLoading(true);
        axios
            .get(`/registry/${agentRegistryName}/agent_groups`)
            .then((response) => {
                let results = _.get(response, "data.results", []);
                for (let i = 0; i < _.size(results); i++) {
                    const group = results[i];
                    let icon = _.get(group, "icon", null);
                    if (
                        !_.isEmpty(icon) &&
                        !_.startsWith(icon, "data:image/")
                    ) {
                        icon = _.split(icon, ":");
                    }
                    _.set(group, "icon", icon);
                }
                setAgentGroups(results);
            })
            .finally(() => setLoading(false));
    }, []);
    const { isSocketOpen } = useSocket();
    const [launchGroup, setLaunchGroup] = useState(null);
    const { creatingSession } = appState.session;
    const joinAgentGroupSession = (groupName) => {
        if (!isSocketOpen || creatingSession || !router.isReady) return;
        setLaunchGroup(groupName);
        AppToaster.show({
            message: `Launching ${groupName}`,
            icon: faIcon({ icon: faHourglassStart }),
        });
        appActions.session.createSession({ groupName, router });
    };
    useEffect(() => {
        if (appState.session.joinAgentGroupSession) {
            appActions.session.setState({
                key: "joinAgentGroupSession",
                value: false,
            });
        }
    }, [appState.session.joinAgentGroupSession]); // eslint-disable-line react-hooks/exhaustive-deps
    return (
        <div style={{ height: "100%", overflowY: "auto" }}>
            <div
                style={{
                    margin: "auto",
                    maxWidth: 600,
                    padding: "100px 20px",
                }}
            >
                <H1 style={{ fontSize: 40, marginBottom: 10 }}>
                    <label style={{ color: Colors.BLUE3 }}>Hello</label>
                    {_.isEmpty(name) ? (
                        <label style={{ color: Colors.BLUE3 }}>.</label>
                    ) : (
                        <>
                            <label style={{ color: Colors.BLUE3 }}>,</label>
                            &nbsp;
                            {name}.
                        </>
                    )}
                </H1>
                <H1
                    className={Classes.TEXT_MUTED}
                    style={{ marginBottom: 60, fontSize: 40, opacity: 0.75 }}
                >
                    How can I help you today?
                </H1>
                {loading ? (
                    <>
                        {LOADING_PLACEMENT}
                        {LOADING_PLACEMENT}
                    </>
                ) : (
                    agentGroups.map((agentGroup, index) => {
                        let opacity = creatingSession ? 0.6 : null;
                        return (
                            <Card
                                key={index}
                                style={{
                                    position: "relative",
                                    marginBottom: 20,
                                    marginLeft: 1,
                                    marginRight: 1,
                                    display: "flex",
                                    gap: 20,
                                    padding: 15,
                                    whiteSpace: "pre-wrap",
                                    cursor: "pointer",
                                    opacity: !isSocketOpen ? 0.6 : null,
                                    pointerEvents:
                                        creatingSession || !isSocketOpen
                                            ? "none"
                                            : null,
                                }}
                                className="agent-group-row"
                                onClick={() =>
                                    joinAgentGroupSession(agentGroup.name)
                                }
                            >
                                <Card style={{ ...ENTITY_ICON_40, opacity }}>
                                    <EntityIcon entity={agentGroup} />
                                </Card>
                                <div
                                    style={{
                                        width: `calc(100% - 120px)`,
                                        opacity,
                                    }}
                                >
                                    {_.get(agentGroup, "description", "-")}
                                </div>
                                <div
                                    className="agent-group-row-actions"
                                    style={ROW_ACTION_STYLE}
                                >
                                    <Tooltip
                                        content="Edit"
                                        minimal
                                        placement="left"
                                    >
                                        <Button
                                            intent={Intent.PRIMARY}
                                            icon={faIcon({ icon: faPen })}
                                            onClick={(event) => {
                                                event.stopPropagation();
                                                router.push(
                                                    `/registry/${agentRegistryName}/agent_group/${agentGroup.name}`
                                                );
                                            }}
                                            size="large"
                                            variant="minimal"
                                            disabled={creatingSession}
                                        />
                                    </Tooltip>
                                </div>
                                {creatingSession &&
                                    _.isEqual(launchGroup, agentGroup.name) && (
                                        <Button
                                            size="large"
                                            style={ROW_ACTION_STYLE}
                                            variant="minimal"
                                            loading={creatingSession}
                                        />
                                    )}
                            </Card>
                        );
                    })
                )}
                {permissions.canWriteAgentRegistry ? (
                    <Link
                        className="no-link-decoration"
                        href={`/registry/${agentRegistryName}/agent_group/new`}
                    >
                        <Button
                            disabled={creatingSession}
                            className={loading ? Classes.SKELETON : null}
                            variant="minimal"
                            alignText={Alignment.START}
                            fill
                            size="large"
                            icon={faIcon({ icon: faPlus })}
                            text="Add"
                        />
                    </Link>
                ) : null}
            </div>
        </div>
    );
}

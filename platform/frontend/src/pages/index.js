import { ENTITY_ICON_40 } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import { SocketContext } from "@/components/contexts/socket-context";
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
} from "@blueprintjs/core";
import {
    faHourglassStart,
    faPlus,
    faSatelliteDish,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext, useEffect, useState } from "react";
export default function LaunchScreen() {
    const { user, permissions } = useContext(AuthContext);
    const { appState, appActions } = useContext(AppContext);
    const router = useRouter();
    const name = _.get(user, "name", null);
    const [agentGroups, setAgentGroups] = useState([]);
    const [loading, setLoading] = useState(true);
    const { authenticating } = useContext(SocketContext);
    const LOADING_PLACEMENT = (
        <Card className={Classes.SKELETON} style={{ marginBottom: 20 }}>
            &nbsp;
        </Card>
    );
    useEffect(() => {
        setLoading(true);
        axios
            .get(
                `/registry/${process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent_groups`
            )
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
    const { socket, reconnectWs, isSocketOpen } = useSocket();
    const [launchGroup, setLaunchGroup] = useState(null);
    const { creatingSession } = appState.session;
    const joinAgentGroupSession = (groupName) => {
        if (!isSocketOpen || creatingSession) return;
        setLaunchGroup(groupName);
        AppToaster.show({
            message: `Launching ${groupName}`,
            icon: faIcon({ icon: faHourglassStart }),
        });
        appActions.session.createSession({ socket, groupName });
    };
    useEffect(() => {
        if (appState.session.joinAgentGroupSession) {
            router.push("/sessions");
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
                {!isSocketOpen ? (
                    <Button
                        loading={
                            (!_.isNil(socket) &&
                                _.isEqual(
                                    socket.readyState,
                                    WebSocket.CONNECTING
                                )) ||
                            authenticating
                        }
                        style={{ marginBottom: 20 }}
                        text="Connect"
                        alignText="left"
                        onClick={reconnectWs}
                        large
                        intent={Intent.PRIMARY}
                        icon={faIcon({ icon: faSatelliteDish })}
                    />
                ) : null}
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
                                    opacity: !isSocketOpen ? 0.54 : null,
                                    pointerEvents:
                                        creatingSession || !isSocketOpen
                                            ? "none"
                                            : null,
                                }}
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
                                {creatingSession &&
                                _.isEqual(launchGroup, agentGroup.name) ? (
                                    <Button
                                        large
                                        style={{
                                            position: "absolute",
                                            right: 15,
                                        }}
                                        minimal
                                        loading={creatingSession}
                                    />
                                ) : null}
                            </Card>
                        );
                    })
                )}
                {permissions.canWriteAgentRegistry ? (
                    <Link
                        className="no-link-decoration"
                        href={`/registry/${process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent_group/new`}
                    >
                        <Button
                            disabled={creatingSession}
                            className={loading ? Classes.SKELETON : null}
                            minimal
                            alignText={Alignment.LEFT}
                            fill
                            large
                            icon={faIcon({ icon: faPlus })}
                            text="Add"
                        />
                    </Link>
                ) : null}
            </div>
        </div>
    );
}

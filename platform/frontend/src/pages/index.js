import { ENTITY_ICON_40 } from "@/components/constant";
import { AuthContext } from "@/components/contexts/auth-context";
import EntityIcon from "@/components/entity/EntityIcon";
import { faIcon } from "@/components/icon";
import {
    Alignment,
    Button,
    Card,
    Classes,
    Colors,
    H1,
} from "@blueprintjs/core";
import { faPlus } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import Link from "next/link";
import { useContext, useEffect, useState } from "react";
export default function LaunchScreen() {
    const { user, permissions } = useContext(AuthContext);
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
            .finally(() => {
                setLoading(false);
            });
    }, []);
    return (
        <div
            style={{
                margin: "auto",
                maxWidth: 600,
                marginTop: 100,
                padding: 20,
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
                agentGroups.map((agentGroup) => (
                    <Card
                        style={{
                            cursor: "pointer",
                            marginBottom: 20,
                            marginLeft: 1,
                            marginRight: 1,
                            display: "flex",
                            gap: 20,
                            padding: 15,
                            whiteSpace: "pre-wrap",
                        }}
                    >
                        <Card style={ENTITY_ICON_40}>
                            <EntityIcon entity={agentGroup} />
                        </Card>
                        <div>{_.get(agentGroup, "description", "-")}</div>
                    </Card>
                ))
            )}
            {permissions.canWriteAgentRegistry ? (
                <Link
                    className="no-link-decoration"
                    href={`/registry/${process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent_group/new`}
                >
                    <Button
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
    );
}

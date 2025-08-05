import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";
import {
    Button,
    ButtonVariant,
    Classes,
    Colors,
    H1,
    Overlay2,
    Size,
} from "@blueprintjs/core";
import { faPlus } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import NewEntity from "../registries/NewEntity";
import { CardListCallout } from "../ux/CardListCallout";
import AgentGroupCard from "./AgentGroupCard";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
function ApplicationContainer({ width, height }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const { user } = useAuthStore(
        useShallow((state) => ({ user: state.user }))
    );
    const userName = _.get(user, "name", null);
    const [loading, setLoading] = useState(false);
    const [agentGroups, setAgentGroups] = useState([]);
    const [showNewEntity, setShowNewEntity] = useState(false);
    useEffect(() => {
        setLoading(true);
        axios
            .get(`/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent_groups`)
            .then((response) => {
                setAgentGroups(_.get(response, "data.results", []));
            })
            .finally(() => setLoading(false));
    }, []);
    const callback = (entity) => {
        setShowNewEntity(false);
        setAgentGroups([...agentGroups, entity]);
    };
    return (
        <div style={{ width, height }}>
            <Overlay2
                onClose={() => {
                    setShowNewEntity(false);
                }}
                isOpen={showNewEntity}
                usePortal={false}
                enforceFocus={false}
                transitionDuration={0}
            >
                <div
                    className="custom-card center-center"
                    style={{
                        width: 800,
                        padding: 20,
                        overflowY: "auto",
                        height: "calc(100% - 40px)",
                        maxWidth: "calc(100% - 40px)",
                    }}
                >
                    <NewEntity callback={callback} type="agent_group" />
                </div>
            </Overlay2>
            <div
                className="full-parent-dimension"
                style={{
                    padding: 20,
                    position: "relative",
                    overflowY: "auto",
                    backgroundColor: darkMode ? Colors.BLACK : null,
                }}
            >
                <H1 style={{ fontSize: 40, marginBottom: 10 }}>
                    <label style={{ color: Colors.BLUE3 }}>Hello</label>
                    {_.isEmpty(userName) ? (
                        <label style={{ color: Colors.BLUE3 }}>.</label>
                    ) : (
                        <>
                            <label style={{ color: Colors.BLUE3 }}>,</label>
                            &nbsp;
                            {userName}.
                        </>
                    )}
                </H1>
                <H1
                    className={Classes.TEXT_MUTED}
                    style={{ fontSize: 40, opacity: 0.75 }}
                >
                    How can I help you today?
                </H1>
                <div style={{ marginTop: 20 }}>
                    <CardListCallout />
                </div>
                <div
                    style={{ marginTop: 20 }}
                    className="responsive-grid-container"
                >
                    {agentGroups.map((agentGroup, index) => (
                        <div key={index} className="grid-item">
                            <AgentGroupCard agentGroup={agentGroup} />
                        </div>
                    ))}
                    <Button
                        onClick={() => {
                            setShowNewEntity(true);
                        }}
                        icon={<FAIcon icon={faPlus} />}
                        size={Size.LARGE}
                        fill
                        variant={ButtonVariant.MINIMAL}
                        text="Add application"
                    />
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(ApplicationContainer);

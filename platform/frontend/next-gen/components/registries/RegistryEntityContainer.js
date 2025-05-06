import { useAppStore } from "@/stores/app-store";
import { Colors } from "@blueprintjs/core";
import _ from "lodash";
import { useEffect, useState } from "react";
import { useContainerContext } from "../contexts/ContainerContext";
import withAutoSizer from "../hocs/withAutoSizer";
import Breadcrumbs from "./Breadcrumbs";
import AgentEntity from "./agents/AgentEntity";
function RegistryEntityContainer({ width, height, entity }) {
    const [breadcrumbs, setBreadcrumbs] = useState([]);
    const { containerId } = useContainerContext();
    const darkMode = useAppStore((state) => state.darkMode);
    useEffect(() => {
        const { name, type, scope } = entity;
        let crumbs = [{ name, type, scope }];
        _.set(crumbs, [0, "start"], true);
        _.set(crumbs, [0, "end"], true);
        setBreadcrumbs(crumbs);
    }, [entity]);
    const current = _.last(breadcrumbs);
    const name = _.get(current, "name", null);
    const type = _.get(current, "type", null);
    return (
        <div
            style={{
                width,
                height,
                backgroundColor: darkMode ? Colors.BLACK : null,
            }}
        >
            <div
                className="full-parent-dimension"
                style={{
                    padding: 20,
                    position: "relative",
                    overflowY: "auto",
                }}
            >
                <Breadcrumbs crumbs={breadcrumbs} />
                <div style={{ marginTop: 20 }}>
                    {_.isEqual(type, "agent") && <AgentEntity name={name} />}
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(RegistryEntityContainer);

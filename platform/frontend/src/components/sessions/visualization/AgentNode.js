import { ENTITY_ICON_40 } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import EntityIcon from "@/components/entity/EntityIcon";
import { Card } from "@blueprintjs/core";
import { Handle, Position } from "@xyflow/react";
import _ from "lodash";
import { useContext } from "react";
export default function AgentNode({ data }) {
    const { appState } = useContext(AppContext);
    return (
        <Card style={{ padding: 10, fontFamily: "monospace, monospace" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <Card style={ENTITY_ICON_40}>
                    <EntityIcon
                        entity={{
                            type: "agent",
                            icon: _.get(appState, [
                                "agent",
                                "icon",
                                data.label,
                            ]),
                        }}
                    />
                </Card>
                {data.label}
            </div>
            {_.get(data, "output", false) ? (
                <Handle type="target" position={Position.Top} />
            ) : null}
            {_.get(data, "input", false) ? (
                <Handle type="source" position={Position.Bottom} />
            ) : null}
        </Card>
    );
}

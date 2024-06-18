import { AppContext } from "@/components/contexts/app-context";
import Breadcrumbs from "@/components/entity/Breadcrumbs";
import NewEntity from "@/components/entity/NewEntity";
import { useContext } from "react";
export default function New() {
    const { appState } = useContext(AppContext);
    const agentRegistryName = appState.agent.registryName;
    return (
        <div style={{ height: "100%", overflowY: "auto" }}>
            <div style={{ margin: "20px 20px 10px" }}>
                <Breadcrumbs
                    breadcrumbs={[
                        {
                            href: `/registry/${agentRegistryName}/agents`,
                            start: true,
                            text: "registry/ default",
                        },
                    ]}
                />
            </div>
            <NewEntity type="agent" />
        </div>
    );
}

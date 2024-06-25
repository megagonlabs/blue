import Breadcrumbs from "@/components/entity/Breadcrumbs";
import NewEntity from "@/components/entity/NewEntity";
export default function New() {
    const agentRegistryName = process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME;
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

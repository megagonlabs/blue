import RegistryBreadcrumbs from "@/components/registry/RegistryBreadcrumbs";
import _ from "lodash";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import AgentEntity from "./agents/AgentEntity";
export default function RegistryEntity() {
    const router = useRouter();
    const [breadcrumbs, setBreadcrumbs] = useState([]);
    useEffect(() => {
        if (_.isEmpty(router.query)) return;
        let { params } = router.query;
        let crumbs = [],
            basePath = "",
            key = null,
            value = null;
        for (var i = 0; i < params.length; i += 2) {
            key = params[i];
            value = params[i + 1];
            basePath += `/${key}/${value}`;
            crumbs.push({
                href: basePath,
                text: `${key} / ${value}`,
                start: _.isEqual(i, 0),
                end: i + 2 >= params.length,
            });
        }
        setBreadcrumbs(crumbs);
    }, [router]);
    return (
        <>
            <div style={{ height: "100%", overflowY: "auto" }}>
                <div style={{ margin: 20 }}>
                    <RegistryBreadcrumbs breadcrumbs={breadcrumbs} />
                </div>
                <div style={{ margin: 20 }}>
                    {_.startsWith(router.asPath, "/agents") ? (
                        <AgentEntity />
                    ) : null}
                </div>
            </div>
        </>
    );
}

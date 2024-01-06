import InputEntity from "@/components/agents/InputEntity";
import OutputEntity from "@/components/agents/OutputEntity";
import CollectionEntity from "@/components/data/CollectionEntity";
import DataEntity from "@/components/data/DataEntity";
import DatabaseEntity from "@/components/data/DatabaseEntity";
import RegistryBreadcrumbs from "@/components/registry/RegistryBreadcrumbs";
import _ from "lodash";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import AgentEntity from "../components/agents/AgentEntity";
export default function RegistryEntity() {
    const router = useRouter();
    const [breadcrumbs, setBreadcrumbs] = useState([]);
    const [entityType, setEntityType] = useState(null);
    useEffect(() => {
        if (_.isEmpty(router.query)) return;
        let { params } = router.query;
        let crumbs = [],
            basePath = "",
            key = null,
            value = null,
            type = "";
        for (var i = 0; i < params.length; i += 2) {
            key = params[i];
            value = params[i + 1];
            basePath += `/${key}/${value}`;
            if (i > 0) {
                type += `/${key}`;
            }
            crumbs.push({
                href: basePath,
                text: `${key}/ ${value}`,
                start: _.isEqual(i, 0),
                end: i + 2 >= params.length,
            });
        }
        setEntityType(type);
        setBreadcrumbs(crumbs);
    }, [router]);
    return (
        <>
            <div style={{ height: "100%", overflowY: "auto" }}>
                <div style={{ margin: "20px 20px 10px" }}>
                    <RegistryBreadcrumbs breadcrumbs={breadcrumbs} />
                </div>
                {_.isEqual(entityType, "/agent") ? <AgentEntity /> : null}
                {_.isEqual(entityType, "/agent/input") ? <InputEntity /> : null}
                {_.isEqual(entityType, "/agent/output") ? (
                    <OutputEntity />
                ) : null}
                {_.isEqual(entityType, "/source") ? <DataEntity /> : null}
                {_.isEqual(entityType, "/source/database") ? (
                    <DatabaseEntity />
                ) : null}
                {_.isEqual(entityType, "/source/database/collection") ? (
                    <CollectionEntity />
                ) : null}
            </div>
        </>
    );
}

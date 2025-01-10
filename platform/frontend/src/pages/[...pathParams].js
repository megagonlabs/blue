import AgentGroupEntity from "@/components/agents/agent_groups/AgentGroupEntity";
import AgentEntity from "@/components/agents/AgentEntity";
import InputEntity from "@/components/agents/InputEntity";
import OutputEntity from "@/components/agents/OutputEntity";
import { ENTITY_TYPE_LOOKUP } from "@/components/constant";
import CollectionEntity from "@/components/data/CollectionEntity";
import DatabaseEntity from "@/components/data/DatabaseEntity";
import EntityEntity from "@/components/data/EntityEntity";
import RelationEntity from "@/components/data/RelationEntity";
import SourceEntity from "@/components/data/SourceEntity";
import Breadcrumbs from "@/components/entity/Breadcrumbs";
import ModelEntity from "@/components/model/ModelEntity";
import OperatorEntity from "@/components/operator/OperatorEntity";
import _ from "lodash";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
export default function RegistryEntity() {
    const router = useRouter();
    const [breadcrumbs, setBreadcrumbs] = useState([]);
    const [entityType, setEntityType] = useState(null);
    useEffect(() => {
        if (_.isEmpty(router.query)) return;
        let { pathParams } = router.query;
        let crumbs = [],
            basePath = "",
            key = null,
            value = null,
            type = "";
        for (var i = 0; i < pathParams.length; i += 2) {
            key = pathParams[i];
            value = pathParams[i + 1];
            basePath += `/${key}/${value}`;
            if (i > 0) {
                type += `/${key}`;
            }
            crumbs.push({
                href: basePath,
                text: `${key}/ ${value}`,
                icon: _.has(ENTITY_TYPE_LOOKUP, key)
                    ? ENTITY_TYPE_LOOKUP[key].icon
                    : null,
                start: _.isEqual(i, 0),
                end: i + 2 >= pathParams.length,
            });
        }
        while (type.includes("/agent/agent")) {
            type = type.replace("/agent/agent", "/agent");
        }
        setEntityType(type);
        const crumb0 = _.get(crumbs, 0, {});
        let baseHref = _.nth(_.split(type, "/"), 1);
        if (_.has(ENTITY_TYPE_LOOKUP, [baseHref, "backtrackCrumb"])) {
            baseHref = _.get(
                ENTITY_TYPE_LOOKUP,
                [baseHref, "backtrackCrumb"],
                baseHref
            );
        }
        _.set(crumbs, 0, {
            ...crumb0,
            href: crumb0.href + "/" + baseHref,
        });
        setBreadcrumbs(crumbs);
    }, [router]);
    const ENTITY_TYPE_TO_COMPONENT = {
        "/agent": <AgentEntity />,
        "/agent_group/agent": <AgentEntity />,
        "/agent_group": <AgentGroupEntity />,
        "/agent/input": <InputEntity />,
        "/agent_group/agent/input": <InputEntity />,
        "/agent/output": <OutputEntity />,
        "/agent_group/agent/output": <OutputEntity />,
        "/operator": <OperatorEntity />,
        "/model": <ModelEntity />,
        "/data": <SourceEntity />,
        "/data/database": <DatabaseEntity />,
        "/data/database/collection": <CollectionEntity />,
        "/data/database/collection/entity": <EntityEntity />,
        "/data/database/collection/relation": <RelationEntity />,
    };
    return (
        <div style={{ height: "100%", overflowY: "auto" }}>
            <div style={{ margin: "20px 20px 10px" }}>
                <Breadcrumbs breadcrumbs={breadcrumbs} />
            </div>
            {_.get(ENTITY_TYPE_TO_COMPONENT, entityType, null)}
        </div>
    );
}

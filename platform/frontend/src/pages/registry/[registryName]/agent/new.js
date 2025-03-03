import {
    ENTITY_TYPE_LOOKUP,
    REGISTRY_NESTING_SEPARATOR,
} from "@/components/constant";
import Breadcrumbs from "@/components/entity/Breadcrumbs";
import NewEntity from "@/components/entity/NewEntity";
import {
    axiosErrorToast,
    constructSavePropertyRequests,
    settlePromises,
    shallowDiff,
} from "@/components/helper";
import { AppToaster } from "@/components/toaster";
import { Card, Intent } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
export default function New() {
    const router = useRouter();
    const [breadcrumbs, setBreadcrumbs] = useState([]);
    const [entity, setEntity] = useState({
        name: "",
        properties: {},
        description: "",
    });
    const [created, setCreated] = useState(false);
    const [loading, setLoading] = useState(false);
    const [jsonError, setJsonError] = useState(false);
    const urlPrefix = `/registry/${process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent`;
    const [namePrefix, setNamePrefix] = useState("");
    const updateEntity = ({ path, value }) => {
        let newEntity = _.cloneDeep(entity);
        _.set(newEntity, path, value);
        setEntity(newEntity);
    };
    const saveEntity = () => {
        if (!router.isReady) return;
        setLoading(true);
        const fullAgentName = `${namePrefix}${entity.name}`;
        axios[created ? "put" : "post"](`${urlPrefix}/${fullAgentName}`, {
            name: fullAgentName,
            description: entity.description,
        })
            .then(() => {
                setCreated(true);
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `Created ${entity.name} agent`,
                });
                const difference = shallowDiff({}, entity.properties);
                settlePromises(
                    constructSavePropertyRequests({
                        axios,
                        url: `${urlPrefix}/${entity.name}/property`,
                        difference,
                        properties: entity.properties,
                    }),
                    ({ error }) => {
                        if (!error) {
                            const nextUrl = router.asPath
                                .split("?")[0]
                                .replace("/new", `/${fullAgentName}`);
                            router.push(nextUrl);
                        }
                        setLoading(false);
                    }
                );
            })
            .catch((error) => {
                axiosErrorToast(error);
                setLoading(false);
            });
    };
    useEffect(() => {
        if (_.isEmpty(router.query)) return;
        const pathParams = router.asPath
            .split("?")[0]
            .split("/")
            .filter((param) => !_.isEmpty(param))
            .slice(0, -2);
        let crumbs = [],
            basePath = "",
            key = null,
            value = null,
            type = "";
        for (var i = 0; i < _.size(pathParams); i += 2) {
            key = pathParams[i];
            value = pathParams[i + 1];
            basePath += `/${key}/${value}`;
            if (i > 0) type += `/${key}`; // eslint-disable-line no-unused-vars
            crumbs.push({
                href: basePath,
                text: `${key}/ ${value}`,
                icon: _.has(ENTITY_TYPE_LOOKUP, key)
                    ? ENTITY_TYPE_LOOKUP[key].icon
                    : null,
                start: _.isEqual(i, 0),
                end: false,
            });
        }
        const crumb0 = _.get(crumbs, 0, {});
        // special case
        _.set(crumbs, 0, { ...crumb0, href: crumb0.href + "/agent" });
        setBreadcrumbs(crumbs);
        if (!_.isEmpty(value) && _.size(pathParams) > 2)
            setNamePrefix(`${value}${REGISTRY_NESTING_SEPARATOR}`);
    }, [router]);
    return (
        <div style={{ height: "100%", overflowY: "auto" }}>
            <Card
                className="full-parent-width"
                style={{
                    padding: "15px 20px",
                    top: 0,
                    left: 0,
                    position: "absolute",
                    zIndex: 1,
                }}
            >
                <Breadcrumbs breadcrumbs={breadcrumbs} />
            </Card>
            <div style={{ marginTop: 70 }}>
                <NewEntity
                    type="agent"
                    namePrefix={namePrefix}
                    updateEntity={updateEntity}
                    saveEntity={saveEntity}
                    entity={entity}
                    loading={loading}
                    jsonError={jsonError}
                    setJsonError={setJsonError}
                    urlPrefix={urlPrefix}
                    setEntity={setEntity}
                />
            </div>
        </div>
    );
}

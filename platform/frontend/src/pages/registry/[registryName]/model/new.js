import { ENTITY_TYPE_LOOKUP } from "@/components/constant";
import Breadcrumbs from "@/components/entity/Breadcrumbs";
import NewEntity from "@/components/entity/NewEntity";
import {
    axiosErrorToast,
    constructSavePropertyRequests,
    populateRouterPathname,
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
    const urlPrefix = `/registry/${process.env.NEXT_PUBLIC_MODEL_REGISTRY_NAME}/model`;
    const updateEntity = ({ path, value }) => {
        let newEntity = _.cloneDeep(entity);
        _.set(newEntity, path, value);
        setEntity(newEntity);
    };
    const saveEntity = () => {
        if (!router.isReady) return;
        setLoading(true);
        axios[created ? "put" : "post"](`${urlPrefix}/${entity.name}`, {
            name: entity.name,
            description: entity.description,
        })
            .then(() => {
                setCreated(true);
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `Created ${entity.name} model`,
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
                            router.push(`${urlPrefix}/${entity.name}`);
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
        const pathParams = populateRouterPathname(router)
            .split("/")
            .filter((param) => !_.isEmpty(param))
            .slice(0, -2);
        let crumbs = [],
            basePath = "",
            key = null,
            value = null,
            type = "";
        for (var i = 0; i < pathParams.length; i += 2) {
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
        _.set(crumbs, 0, { ...crumb0, href: crumb0.href + "/model" });
        setBreadcrumbs(crumbs);
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
                    type="model"
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

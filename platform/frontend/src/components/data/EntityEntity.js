import EntityDescription from "@/components/entity/EntityDescription";
import EntityMain from "@/components/entity/EntityMain";
import EntityProperties from "@/components/entity/EntityProperties";
import axios from "axios";
import _ from "lodash";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
export default function EntityEntity() {
    const router = useRouter();
    const [entity, setEntity] = useState({ type: "entity" });
    const [loading, setLoading] = useState(true);
    const routerQueryPath =
        "/" + _.get(router, "query.pathParams", []).join("/");
    useEffect(() => {
        if (!router.isReady) return;
        axios.get(routerQueryPath).then((response) => {
            setEntity(_.get(response, "data.result", {}));
            setLoading(false);
        });
    }, [router, routerQueryPath]);
    return (
        <div style={{ padding: "10px 20px 20px" }}>
            <EntityMain entity={entity} loading={loading} />
            <EntityDescription entity={entity} loading={loading} />
            <EntityProperties entity={entity} loading={loading} />
        </div>
    );
}

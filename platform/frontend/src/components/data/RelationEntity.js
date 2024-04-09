import EntityDescription from "@/components/entity/EntityDescription";
import EntityMain from "@/components/entity/EntityMain";
import EntityProperties from "@/components/entity/EntityProperties";
import axios from "axios";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
export default function RelationEntity() {
    const router = useRouter();
    const [entity, setEntity] = useState({});
    useEffect(() => {
        if (!router.isReady) return;
        axios.get(router.asPath).then((response) => {
            setEntity(_.get(response, "data.result", {}));
        });
    }, [router]);
    return (
        <div style={{ padding: "10px 20px 20px" }}>
            <EntityMain entity={entity} />
            <EntityDescription entity={entity} />
            <EntityProperties entity={entity} />
        </div>
    );
}

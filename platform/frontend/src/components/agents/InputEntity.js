import axios from "axios";
import _ from "lodash";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import EntityDescription from "../entity/EntityDescription";
import EntityMain from "../entity/EntityMain";
import EntityProperties from "../entity/EntityProperties";
export default function InputEntity() {
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

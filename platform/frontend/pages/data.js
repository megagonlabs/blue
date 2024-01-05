import { AppContext } from "@/components/app-context";
import RegistryList from "@/components/registries/RegistryList";
import { Card, H4, HTMLSelect } from "@blueprintjs/core";
import { useContext, useEffect } from "react";
export default function Data() {
    const { appActions } = useContext(AppContext);
    useEffect(() => {
        // appActions.data.getData();
    }, []);
    return (
        <>
            <Card
                style={{
                    borderRadius: 0,
                    padding: 15,
                    display: "flex",
                    alignItems: "center",
                }}
            >
                <H4 style={{ margin: "0px 15px 0px 0px" }}>Data Registry</H4>
                <HTMLSelect minimal>
                    <option value="">default</option>
                </HTMLSelect>
            </Card>
            <div
                style={{
                    height: "calc(100% - 61px)",
                    overflowY: "auto",
                    marginTop: 2,
                }}
            >
                <RegistryList type="data" />
            </div>
        </>
    );
}

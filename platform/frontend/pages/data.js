import { AppContext } from "@/components/app-context";
import RegistryList from "@/components/registries/RegistryList";
import { H4, HTMLSelect } from "@blueprintjs/core";
import { useContext, useEffect } from "react";
export default function Data() {
    const { appActions } = useContext(AppContext);
    useEffect(() => {
        // appActions.data.getData();
    }, []);
    return (
        <>
            <div
                style={{
                    padding: "15px 15px 7.5px 15px",
                    display: "flex",
                    alignItems: "center",
                }}
            >
                <H4 style={{ margin: "0px 15px 0px 0px" }}>Data Registry</H4>
                <HTMLSelect minimal>
                    <option value="">default</option>
                </HTMLSelect>
            </div>
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

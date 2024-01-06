import { AppContext } from "@/components/app-context";
import RegistryList from "@/components/registry/RegistryList";
import { H4, HTMLSelect } from "@blueprintjs/core";
import { useContext, useEffect } from "react";
export default function Data() {
    const { appState, appActions } = useContext(AppContext);
    useEffect(() => {
        appActions.data.getList();
    }, []);
    return (
        <>
            <div
                style={{
                    padding: "20px 20px 10px 20px",
                    display: "flex",
                    alignItems: "center",
                }}
            >
                <H4 style={{ margin: "0px 20px 0px 0px" }}>Data Registry</H4>
                <HTMLSelect
                    minimal
                    value={appState.data.registryName}
                    onChange={(event) => {}}
                >
                    <option value="default">default</option>
                </HTMLSelect>
            </div>
            <div
                style={{
                    height: "calc(100% - 61px)",
                    overflowY: "auto",
                }}
            >
                <RegistryList type="data" />
            </div>
        </>
    );
}

import { OverlayToaster, Position } from "@blueprintjs/core";
import _ from "lodash";
import { createContext, useContext, useEffect, useState } from "react";
const ToasterContext = createContext();
export const useToaster = () => {
    return useContext(ToasterContext);
};
export const ToasterProvider = ({ children }) => {
    const [toasters, setToasters] = useState({ appToaster: null });
    const [initialized, setInitialized] = useState(false);
    useEffect(() => {
        const status = [!_.isNull(toasters.appToaster)];
        setInitialized(_.every(status, Boolean));
    }, [toasters]);
    useEffect(() => {
        const createToasters = async () => {
            if (typeof window !== "undefined") {
                const appToasterInstance = await OverlayToaster.create({
                    position: Position.BOTTOM,
                });
                setToasters({ appToaster: appToasterInstance });
            }
        };
        createToasters();
    }, []);
    return (
        <ToasterContext.Provider value={{ ...toasters, initialized }}>
            {children}
        </ToasterContext.Provider>
    );
};

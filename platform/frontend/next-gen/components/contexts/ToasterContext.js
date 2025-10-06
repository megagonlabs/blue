import { Intent, OverlayToaster, Position } from "@blueprintjs/core";
import {
    faCopy,
    faExclamation,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { createContext, useContext, useEffect, useState } from "react";
import { FAIcon } from "../FAIcon";
const ToasterContext = createContext();
export const useToaster = () => {
    return useContext(ToasterContext);
};
export const ToasterProvider = ({ children }) => {
    const [toasters, setToasters] = useState({
        appToaster: null,
        progressToaster: null,
    });
    const [initialized, setInitialized] = useState(false);
    useEffect(() => {
        const status = [
            !_.isNull(toasters.appToaster),
            !_.isNull(toasters.progressToaster),
        ];
        setInitialized(_.every(status, Boolean));
    }, [toasters]);
    useEffect(() => {
        const createToasters = async () => {
            if (typeof window !== "undefined") {
                const appToasterInstance = await OverlayToaster.create({
                    position: Position.BOTTOM,
                });
                const progressToasterInstance = await OverlayToaster.create({
                    position: Position.TOP,
                });
                setToasters({
                    appToaster: appToasterInstance,
                    progressToaster: progressToasterInstance,
                });
            }
        };
        createToasters();
    }, []);
    const showAxiosErrorToast = (error) => {
        let message = "";
        try {
            message = `${error.name}: ${error.message}`;
            // the request was made and the server responded with a status code
            // that falls out of the range of 2xx
            if (error.response)
                message = `[${error.response.status} ${
                    error.response.statusText
                }]: ${_.get(error, "response.data.message", "-")}`;
        } catch (error) {
            message = "Request Error";
        }
        if (!_.isNull(toasters.appToaster)) {
            toasters.appToaster.show({
                icon: <FAIcon icon={faExclamation} />,
                intent: Intent.DANGER,
                message: <div className="multiline-ellipsis-5">{message}</div>,
                action: {
                    icon: <FAIcon icon={faCopy} />,
                    onClick: () => {
                        copy(message);
                    },
                    text: "Copy",
                },
            });
        }
    };
    return (
        <ToasterContext.Provider
            value={{ ...toasters, initialized, showAxiosErrorToast }}
        >
            {children}
        </ToasterContext.Provider>
    );
};

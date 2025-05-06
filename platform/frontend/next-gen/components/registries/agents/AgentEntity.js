import {
    HEX_TRANSPARENCY,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import { useAppStore } from "@/stores/app-store";
import { Classes, Colors } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import RegistryEntityIcon from "../RegistryEntityIcon";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
const MAIN_INFO_STYLES = {
    height: 40,
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    maxWidth: "100%",
};
export default function AgentEntity({ name }) {
    const [agent, setAgent] = useState(null);
    const darkMode = useAppStore((state) => state.darkMode);
    useEffect(() => {
        axios
            .get(`/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/agent/${name}`)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                if (_.isEmpty(result)) {
                    setAgent(null);
                } else {
                    setAgent(result);
                }
            });
    }, [name]);
    return (
        <div>
            <div
                style={{
                    backgroundColor: `${Colors.BLUE3}${
                        HEX_TRANSPARENCY[darkMode ? 20 : 10]
                    }`,
                    padding: 20,
                    position: "relative",
                }}
            >
                <div
                    className="padding-0 overflow-hidden custom-card"
                    style={{
                        ...REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
                        position: "absolute",
                        left: 20,
                        top: 20,
                    }}
                >
                    <RegistryEntityIcon content={_.get(agent, "icon", null)} />
                </div>
                <div
                    style={{
                        display: "flex",
                        marginLeft: 60,
                        columnGap: 40,
                        rowGap: 20,
                        flexWrap: "wrap",
                    }}
                >
                    <div style={MAIN_INFO_STYLES}>
                        <div>{_.get(agent, "type")}</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(agent, "name")}
                        </div>
                    </div>
                    <div style={MAIN_INFO_STYLES}>
                        <div className={Classes.TEXT_MUTED}>Display name</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(agent, "properties.display_name", "-")}
                        </div>
                    </div>
                    <div style={MAIN_INFO_STYLES}>
                        <div className={Classes.TEXT_MUTED}>Docker image</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(agent, "properties.image", "-")}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

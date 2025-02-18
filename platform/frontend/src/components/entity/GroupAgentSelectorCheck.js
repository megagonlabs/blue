import { faIcon } from "@/components/icon";
import { Colors } from "@blueprintjs/core";
import { faCheck } from "@fortawesome/pro-solid-svg-icons";
import _ from "lodash";
import { useContext } from "react";
import { AppContext } from "../contexts/app-context";
export default function GroupAgentSelectorCheck({ agent, type }) {
    const { appState } = useContext(AppContext);
    const { agentGroupSelection } = appState.agent;
    const isSelected = _.get(agentGroupSelection, [type, agent], false);
    if (isSelected)
        return faIcon({ icon: faCheck, style: { color: Colors.GREEN3 } });
    return null;
}

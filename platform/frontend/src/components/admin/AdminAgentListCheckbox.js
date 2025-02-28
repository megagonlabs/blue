import { Checkbox } from "@blueprintjs/core";
import _ from "lodash";
import { useContext } from "react";
import { AppContext } from "../contexts/app-context";
export default function AdminAgentListCheckbox({ data, rowIndex }) {
    const { appState, appActions } = useContext(AppContext);
    const selectedAgents = _.get(appState, "admin.selectedAgents", new Set());
    const agent = _.get(data, [rowIndex, "agent"], null);
    const onChange = (event) => {
        if (event.target.checked) {
            appActions.admin.addSelectedAgent(agent);
        } else {
            appActions.admin.removeSelectedAgent(agent);
        }
    };
    return (
        <Checkbox
            onChange={onChange}
            checked={selectedAgents.has(agent)}
            size="large"
            className="margin-0"
        />
    );
}

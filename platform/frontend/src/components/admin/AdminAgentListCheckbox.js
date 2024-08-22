import { Checkbox } from "@blueprintjs/core";
import _ from "lodash";
import { useContext } from "react";
import { AppContext } from "../contexts/app-context";
export default function AdminAgentListCheckbox({ data, rowIndex }) {
    const { appState, appActions } = useContext(AppContext);
    const selectedAgents = _.get(appState, "admin.selectedAgents", new Set());
    const id = _.get(data, [rowIndex, "id"], null);
    const onChange = (event) => {
        if (event.target.checked) {
            appActions.admin.addSelectedAgent(id);
        } else {
            appActions.admin.removeSelectedAgent(id);
        }
    };
    return (
        <Checkbox
            onChange={onChange}
            checked={selectedAgents.has(id)}
            large
            className="margin-0"
        />
    );
}

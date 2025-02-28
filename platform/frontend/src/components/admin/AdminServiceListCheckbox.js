import { Checkbox } from "@blueprintjs/core";
import _ from "lodash";
import { useContext } from "react";
import { AppContext } from "../contexts/app-context";
export default function AdminServiceListCheckbox({ data, rowIndex }) {
    const { appState, appActions } = useContext(AppContext);
    const selectedServices = _.get(
        appState,
        "admin.selectedServices",
        new Set()
    );
    const service = _.get(data, [rowIndex, "service"], null);
    const onChange = (event) => {
        if (event.target.checked) {
            appActions.admin.addSelectedService(service);
        } else {
            appActions.admin.removeSelectedService(service);
        }
    };
    return (
        <Checkbox
            onChange={onChange}
            checked={selectedServices.has(service)}
            size="large"
            className="margin-0"
        />
    );
}

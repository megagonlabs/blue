import { AuthContext } from "@/components/contexts/auth-context";
import { Checkbox } from "@blueprintjs/core";
import _ from "lodash";
import { useContext } from "react";
import { AppContext } from "../contexts/app-context";
export default function ActionCheckbox({ data, rowIndex }) {
    const { appState, appActions } = useContext(AppContext);
    const selectedUsers = _.get(appState, "admin.selectedUsers", new Set());
    const uid = _.get(data, [rowIndex, "uid"], null);
    const { user } = useContext(AuthContext);
    const currentUserUid = _.get(user, "uid", null);
    const onChange = (event) => {
        if (event.target.checked) {
            appActions.admin.addSelectedUser(uid);
        } else {
            appActions.admin.removeSelectedUser(uid);
        }
    };

    if (_.isEqual(uid, currentUserUid)) {
        return null;
    }
    return (
        <Checkbox
            onChange={onChange}
            checked={selectedUsers.has(uid)}
            large
            className="margin-0"
        />
    );
}

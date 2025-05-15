import { useAuthStore } from "@/stores/auth-store";
import { usePlatformStore } from "@/stores/platform-store";
import { Checkbox, Size } from "@blueprintjs/core";
import _ from "lodash";
import { useShallow } from "zustand/react/shallow";
export default function UserCheckbox({ uid }) {
    const user = useAuthStore((state) => state.user);
    const { updateUserTableSelected, selected } = usePlatformStore(
        useShallow((state) => ({
            updateUserTableSelected: state.updateUserTableSelected,
            selected: state.users.selected,
        }))
    );
    const handleOnChange = (event) => {
        updateUserTableSelected({ uid, checked: event.target.checked });
    };
    if (_.isEqual(user.uid, uid)) {
        return null;
    }
    return (
        <Checkbox
            onChange={handleOnChange}
            className="margin-0"
            size={Size.LARGE}
            checked={_.isSet(selected) && selected.has(uid)}
        />
    );
}

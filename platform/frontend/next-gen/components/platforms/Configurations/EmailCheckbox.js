import { useAuthStore } from "@/stores/auth-store";
import { usePlatformStore } from "@/stores/platform-store";
import { Checkbox, Size } from "@blueprintjs/core";
import _ from "lodash";
import { useShallow } from "zustand/react/shallow";
export default function EmailCheckbox({ email }) {
    const user = useAuthStore((state) => state.user);
    const { updateEmailTableSelected, selectedEmails } = usePlatformStore(
        useShallow((state) => ({
            updateEmailTableSelected: state.updateEmailTableSelected,
            selectedEmails: state.configurations.selectedEmails,
        }))
    );
    const handleOnChange = (event) => {
        updateEmailTableSelected({ email, checked: event.target.checked });
    };
    if (_.isEqual(user.email, email)) {
        return null;
    }
    return (
        <Checkbox
            onChange={handleOnChange}
            className="margin-0"
            size={Size.LARGE}
            checked={_.isSet(selectedEmails) && selectedEmails.has(email)}
        />
    );
}

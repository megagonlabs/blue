import { usePlatformStore } from "@/stores/platform-store";
import { Checkbox, Size } from "@blueprintjs/core";
import { useShallow } from "zustand/react/shallow";
export default function ServiceCheckbox({ serviceName }) {
    const { updateServiceTableSelected, selected } = usePlatformStore(
        useShallow((state) => ({
            updateServiceTableSelected: state.updateServiceTableSelected,
            selected: state.services.selected,
        }))
    );
    const handleOnChange = (event) => {
        updateServiceTableSelected({
            serviceName,
            checked: event.target.checked,
        });
    };
    return (
        <Checkbox
            onChange={handleOnChange}
            className="margin-0"
            size={Size.LARGE}
            checked={_.isSet(selected) && selected.has(serviceName)}
        />
    );
}

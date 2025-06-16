import { usePlatformStore } from "@/stores/platform-store";
import { Checkbox, Size } from "@blueprintjs/core";
import _ from "lodash";
import { useShallow } from "zustand/react/shallow";
export default function AgentCheckbox({ agentName }) {
    const { updateAgentTableSelected, selected } = usePlatformStore(
        useShallow((state) => ({
            selected: state.agents.selected,
            updateAgentTableSelected: state.updateAgentTableSelected,
        }))
    );
    const handleOnChange = (event) => {
        updateAgentTableSelected({ agentName, checked: event.target.checked });
    };
    return (
        <Checkbox
            onChange={handleOnChange}
            className="margin-0"
            size={Size.LARGE}
            checked={_.isSet(selected) && selected.has(agentName)}
        />
    );
}

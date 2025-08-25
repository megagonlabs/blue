import { NonIdealState } from "@blueprintjs/core";
import { faShelvesEmpty } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { FAIcon } from "../FAIcon";
export default function NoResultsFound() {
    return (
        <NonIdealState
            title="No results found"
            description="It seems we can't find any results based on your search."
            icon={<FAIcon size={50} icon={faShelvesEmpty} />}
        />
    );
}

import { faIcon } from "@/components/icon";
import { NonIdealState } from "@blueprintjs/core";
import { faPersonDigging } from "@fortawesome/pro-duotone-svg-icons";
export default function Services() {
    return (
        <>
            <NonIdealState icon={faIcon({ icon: faPersonDigging, size: 50 })} />
        </>
    );
}

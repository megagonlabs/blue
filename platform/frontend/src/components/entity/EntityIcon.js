import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import _ from "lodash";
import Image from "next/image";
import { ENTITY_TYPE_LOOKUP } from "../constant";
import { faIcon } from "../icon";
export default function EntityIcon({ entity }) {
    const { icon, type } = entity;
    if (_.isEqual(_.get(icon, "type", null), "canvas")) {
        // preview <canvas/> element
        return icon;
    } else if (_.startsWith(icon, "data:image/")) {
        return <Image width={40} height={40} src={icon} alt="" />;
    } else if (_.isEmpty(icon) || _.isEmpty(icon[0])) {
        return faIcon({ icon: ENTITY_TYPE_LOOKUP[type].icon, size: 20 });
    }
    return (
        <FontAwesomeIcon
            color={icon[1]}
            style={{ height: 20, width: 20 }}
            icon={["fasds", icon[0]]}
        />
    );
}

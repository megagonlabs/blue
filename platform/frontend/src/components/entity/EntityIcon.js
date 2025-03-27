import { faIcon } from "@/components/icon";
import { Colors } from "@blueprintjs/core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import _ from "lodash";
import Image from "next/image";
import { ENTITY_TYPE_LOOKUP } from "../constant";
export default function EntityIcon({ entity, iconSize = 20 }) {
    const { icon, type } = entity;
    if (_.isEqual(_.get(icon, "type", null), "canvas")) {
        // preview <canvas/> element
        return icon;
    } else if (_.startsWith(icon, "data:image/")) {
        return <Image width={40} height={40} src={icon} alt="" />;
    } else if (_.isEmpty(icon) || _.isEmpty(icon[0])) {
        return faIcon({
            icon: _.get(ENTITY_TYPE_LOOKUP, [type, "icon"], null),
            size: iconSize,
            style: { color: Colors.BLACK },
        });
    }
    return (
        <FontAwesomeIcon
            color={icon[1]}
            style={{ height: iconSize, width: iconSize }}
            icon={["fasds", icon[0]]}
        />
    );
}

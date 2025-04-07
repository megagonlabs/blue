import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import _ from "lodash";
import Image from "next/image";
export default function RegistryEntityIcon({ content }) {
    const isCanvas = _.isEqual(_.get(content, "type", null), "canvas");
    const [icon, color] = _.split(content, ":");
    if (isCanvas) {
        return content;
    } else if (_.startsWith(content, "data:image/")) {
        return <Image width={40} height={40} src={content} alt="" />;
    } else if (_.isEmpty(icon) || _.isEmpty(color)) {
        return null;
    }
    return (
        <FontAwesomeIcon
            color={color}
            style={{ height: 20, width: 20 }}
            icon={["fasds", icon]}
        />
    );
}

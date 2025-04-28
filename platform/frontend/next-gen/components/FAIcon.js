import { Classes } from "@blueprintjs/core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
export const FAIcon = ({ icon, className = [], size = 16, style = {} }) => {
    return (
        <FontAwesomeIcon
            className={classNames(className, Classes.ICON)}
            style={{ ...style, height: size, width: size }}
            icon={icon}
        />
    );
};

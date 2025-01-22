import { Classes } from "@blueprintjs/core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import _ from "lodash";
export const faIcon = (props) => {
    let { icon, className = [], size = 16, style = {} } = props;
    if (_.isEmpty(className)) className = [];
    if (_.isString(className)) className = [className];
    className.push(Classes.ICON);
    return (
        <FontAwesomeIcon
            className={classNames(...className)}
            style={{ ...style, height: size, width: size }}
            icon={icon}
        />
    );
};

import _ from "lodash";
export default function EntityDisplayName({ entity }) {
    const name = _.get(entity, "name", null);
    const displayName = _.get(entity, "properties.display_name", name);
    return !_.isEmpty(displayName) ? displayName : name;
}

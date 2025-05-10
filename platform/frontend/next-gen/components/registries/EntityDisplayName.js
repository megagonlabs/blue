import _ from "lodash";
export default function EntityDisplayName({ entity }) {
    const displayName = _.get(entity, "properties.display_name", entity.name);
    return !_.isEmpty(displayName) ? displayName : entity.name;
}

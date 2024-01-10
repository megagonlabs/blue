const { faCircleA, faServer } = require("@fortawesome/pro-duotone-svg-icons");
module.exports = {
    REGISTRY_TYPE_LOOKUP: {
        data: { icon: faServer, key: "source" },
        agent: { icon: faCircleA, key: "agent" },
    },
};

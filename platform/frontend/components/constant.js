const {
    faCircleA,
    faServer,
    faHeadSideGear,
    faDatabase,
    faFolderOpen,
    faFile,
    faProjectDiagram,
    faArrowRightToArc,
    faArrowRightFromArc,
} = require("@fortawesome/pro-duotone-svg-icons");
module.exports = {
    REGISTRY_TYPE_LOOKUP: {
        data: { icon: faServer, key: "source" },
        agent: { icon: faCircleA, key: "agent" },
    },
    SEARCH_LIST_TYPE_LOOKUP: {
        agent: { icon: faHeadSideGear },
        input: { icon: faArrowRightToArc },
        output: { icon: faArrowRightFromArc },
        source: { icon: faServer },
        database: { icon: faDatabase },
        collection: { icon: faFolderOpen },
        entity: { icon: faFile },
        relation: { icon: faProjectDiagram },
    },
};

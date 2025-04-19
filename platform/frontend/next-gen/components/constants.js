import { Colors } from "@blueprintjs/core";
export const USER_ROLES_LOOKUP = {
        admin: { text: "Administrator" },
        member: { text: "Member" },
        guest: { text: "Guest" },
        developer: { text: "Developer" },
        demo: { text: "Demo" },
    },
    DOCKER_CONTAINER_STATUS_LOOKUP = {
        created: { style: { color: Colors.ORANGE3 } },
        running: { style: { color: Colors.GREEN3 } },
        paused: { style: { color: Colors.RED3 } },
        restarting: { style: { color: Colors.ORANGE3 } },
        exited: { style: { color: Colors.RED3 } },
        removing: { style: { color: Colors.RED3 } },
        dead: { style: { color: Colors.RED3 } },
    },
    MIN_ALLOTMENT_PANE_SIZE = 400,
    MESSAGE_OVERFLOW_THRESHOLD = 200;

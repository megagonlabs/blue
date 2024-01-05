export const defaultState = {
    registryName: "default",
    list: [
        {
            name: "TitleRecommender",
            description:
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            properties: {
                image: "docker-image:latest",
            },
        },
    ],
};
export default function agentReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "agent/list/set":
            return { ...state, list: payload };
        case "agent/registryName/set":
            return { ...state, registryName: payload };
        default:
            return state;
    }
}

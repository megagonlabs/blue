export const defaultState = {
    list: [
        {
            name: "indeed_mongodb",
            description:
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            properties: {
                connection: {
                    host: "localhost",
                    port: 27017,
                    protocol: "mongodb",
                },
            },
        },
    ],
};
export default function dataReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "data/list/set":
            return { ...state, list: payload };
        default:
            return state;
    }
}

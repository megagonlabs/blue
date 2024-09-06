export const defaultState = {
    messages: [],
};
export default function debugReducer(state = defaultState, { type, payload }) {
    switch (type) {
        case "debug/messages/add": {
            return { ...state, messages: [payload, ...state.messages] };
        }
        case "debug/messages/clear": {
            return { ...state, messages: [] };
        }
        default:
            return state;
    }
}

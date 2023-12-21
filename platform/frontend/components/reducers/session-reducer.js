export const defaultState = {};
export default function sessionReducer(
    state = defaultState,
    { type, payload }
) {
    switch (type) {
        default:
            return state;
    }
}

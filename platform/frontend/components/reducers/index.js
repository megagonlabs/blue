import appReducer from "./app-reducer";
export default function rootReducer(state = {}, action) {
    return {
        app: appReducer(state.app, action),
    };
}

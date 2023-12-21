import appReducer from "./app-reducer";
import sessionReducer from "./session-reducer";
export default function rootReducer(state = {}, action) {
    return {
        app: appReducer(state.app, action),
        session: sessionReducer(state.app, action),
    };
}

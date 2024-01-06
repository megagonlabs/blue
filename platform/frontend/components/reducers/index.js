import agentReducer from "./agent-reducer";
import dataReducer from "./data-reducer";
import appReducer from "./app-reducer";
import sessionReducer from "./session-reducer";
export default function rootReducer(state = {}, action) {
    return {
        app: appReducer(state.app, action),
        session: sessionReducer(state.session, action),
        agent: agentReducer(state.agents, action),
        data: dataReducer(state.data, action),
    };
}

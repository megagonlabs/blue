import agentReducer from "@/components/reducers/agent-reducer";
import appReducer from "@/components/reducers/app-reducer";
import dataReducer from "@/components/reducers/data-reducer";
import sessionReducer from "@/components/reducers/session-reducer";
export default function rootReducer(state = {}, action) {
    return {
        app: appReducer(state.app, action),
        session: sessionReducer(state.session, action),
        agent: agentReducer(state.agent, action),
        data: dataReducer(state.data, action),
    };
}

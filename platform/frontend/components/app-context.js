import { createContext, useReducer } from "react";
import { agentAction } from "./actions/agent-action";
import { dataAction } from "./actions/data-action";
import { appAction } from "./actions/app-action";
import { sessionAction } from "./actions/session-action";
import rootReducer from "./reducers";
import { defaultState as agentDefaultState } from "./reducers/agent-reducer";
import { defaultState as dataDefaultState } from "./reducers/data-reducer";
import { defaultState as appDefaultState } from "./reducers/app-reducer";
import { defaultState as sessionDefaultState } from "./reducers/session-reducer";
const AppContext = createContext();
const AppProvider = ({ children }) => {
    const [appState, dispatch] = useReducer(rootReducer, {
        app: appDefaultState,
        session: sessionDefaultState,
        agent: agentDefaultState,
        data:  dataDefaultState,
    });
    const actions = {
        app: { ...appAction(dispatch) },
        session: { ...sessionAction(dispatch) },
        agent: { ...agentAction(dispatch) },
        data: { ...dataAction(dispatch) },
    };
    return (
        <AppContext.Provider
            value={{ appState: appState, appActions: actions }}
        >
            {children}
        </AppContext.Provider>
    );
};
export { AppContext, AppProvider };

import { agentAction } from "@/components/actions/agent-action";
import { appAction } from "@/components/actions/app-action";
import { dataAction } from "@/components/actions/data-action";
import { sessionAction } from "@/components/actions/session-action";
import rootReducer from "@/components/reducers";
import { defaultState as agentDefaultState } from "@/components/reducers/agent-reducer";
import { defaultState as appDefaultState } from "@/components/reducers/app-reducer";
import { defaultState as dataDefaultState } from "@/components/reducers/data-reducer";
import { defaultState as sessionDefaultState } from "@/components/reducers/session-reducer";
import { createContext, useMemo, useReducer } from "react";
const AppContext = createContext();
const AppProvider = ({ children }) => {
    const [appState, dispatch] = useReducer(rootReducer, {
        app: appDefaultState,
        session: sessionDefaultState,
        agent: agentDefaultState,
        data: dataDefaultState,
    });
    const actions = {
        app: { ...appAction(dispatch) },
        session: { ...sessionAction(dispatch) },
        agent: { ...agentAction(dispatch) },
        data: { ...dataAction(dispatch) },
    };
    const store = useMemo(
        () => ({ appState, appActions: actions }),
        [appState]
    );
    return <AppContext.Provider value={store}>{children}</AppContext.Provider>;
};
export { AppContext, AppProvider };

import { adminAction } from "@/components/actions/admin-action";
import { agentAction } from "@/components/actions/agent-action";
import { appAction } from "@/components/actions/app-action";
import { dataAction } from "@/components/actions/data-action";
import { debugAction } from "@/components/actions/debug-action";
import { modelAction } from "@/components/actions/model-action";
import { operatorAction } from "@/components/actions/operator-action";
import { sessionAction } from "@/components/actions/session-action";
import rootReducer from "@/components/reducers";
import { defaultState as adminDS } from "@/components/reducers/admin-reducer";
import { defaultState as agentDS } from "@/components/reducers/agent-reducer";
import { defaultState as appDS } from "@/components/reducers/app-reducer";
import { defaultState as dataDS } from "@/components/reducers/data-reducer";
import { defaultState as debugDS } from "@/components/reducers/debug-reducer";
import { defaultState as modelDS } from "@/components/reducers/model-reducer";
import { defaultState as operatorDS } from "@/components/reducers/operator-reducer";
import { defaultState as sessionDS } from "@/components/reducers/session-reducer";
import { defaultState as trackerDS } from "@/components/reducers/tracker-reducer";
import { createContext, useMemo, useReducer } from "react";
import { trackerAction } from "../actions/tracker-action";
const AppContext = createContext();
const AppProvider = ({ children }) => {
    const [appState, dispatch] = useReducer(rootReducer, {
        app: appDS,
        session: sessionDS,
        agent: agentDS,
        data: dataDS,
        admin: adminDS,
        debug: debugDS,
        operator: operatorDS,
        model: modelDS,
        tracker: trackerDS,
    });
    const actions = {
        app: { ...appAction(dispatch) },
        session: { ...sessionAction(dispatch) },
        agent: { ...agentAction(dispatch) },
        data: { ...dataAction(dispatch) },
        admin: { ...adminAction(dispatch) },
        debug: { ...debugAction(dispatch) },
        operator: { ...operatorAction(dispatch) },
        model: { ...modelAction(dispatch) },
        tracker: { ...trackerAction(dispatch) },
    };
    const store = useMemo(
        () => ({ appState, appActions: actions }),
        [appState]
    );
    return <AppContext.Provider value={store}>{children}</AppContext.Provider>;
};
export { AppContext, AppProvider };

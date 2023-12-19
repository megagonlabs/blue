import { createContext, useReducer } from "react";
import { appAction } from "./actions/app-action";
import rootReducer from "./reducers";
import { defaultState as appDefaultState } from "./reducers/app-reducer";
const AppContext = createContext();
const AppProvider = ({ children }) => {
    const [appState, dispatch] = useReducer(rootReducer, {
        app: appDefaultState,
    });
    const actions = {
        app: { ...appAction(dispatch) },
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

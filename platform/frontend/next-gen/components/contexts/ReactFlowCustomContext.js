import { createContext, useContext } from "react";
const ReactFlowCustomContext = createContext(null);
function ReactFlowCustomProvider({ value, children }) {
    return (
        <ReactFlowCustomContext.Provider value={value}>
            {children}
        </ReactFlowCustomContext.Provider>
    );
}
function useReactFlowCustomContext() {
    return useContext(ReactFlowCustomContext);
}
export {
    ReactFlowCustomContext,
    ReactFlowCustomProvider,
    useReactFlowCustomContext,
};

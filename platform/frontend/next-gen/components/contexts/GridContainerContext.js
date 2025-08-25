import { createContext, useContext } from "react";
const GridContainerContext = createContext(null);
function GridContainerProvider({ value, children }) {
    return (
        <GridContainerContext.Provider value={value}>
            {children}
        </GridContainerContext.Provider>
    );
}
function useGridContainerContext() {
    return useContext(GridContainerContext);
}
export { GridContainerContext, GridContainerProvider, useGridContainerContext };

import { createContext, useContext } from "react";
const ContainerContext = createContext(null);
function ContainerContextProvider({ value, children }) {
    return (
        <ContainerContext.Provider value={value}>
            {children}
        </ContainerContext.Provider>
    );
}
function useContainerContext() {
    return useContext(ContainerContext);
}
export { ContainerContext, ContainerContextProvider, useContainerContext };

export const dataAction = (dispatch) => ({
    getList: () => {
        axios.get("/data").then((response) => {
            dispatch({
                type: "data/list/set",
                payload: _.get(response, "data", []),
            });
        });
    },
    setRegistryName: (payload) => {
        dispatch({
            type: "data/registryName/set",
            payload: payload,
        });
    },
});

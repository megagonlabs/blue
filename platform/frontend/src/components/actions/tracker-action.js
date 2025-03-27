export const trackerAction = (dispatch) => ({
    addTrackerData: (payload) =>
        dispatch({ type: "tracker/data/add", payload }),
    addTracker: (payload) => dispatch({ type: "tracker/add", payload }),
});

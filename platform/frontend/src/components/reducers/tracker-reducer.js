import _ from "lodash";
import { mergeTrackerData } from "../helper";
export const defaultState = { data: {} };
export default function trackerReducer(
    state = defaultState,
    { type, payload }
) {
    let { data } = state;
    switch (type) {
        case "tracker/data/add": {
            const trackerData = _.get(data, payload.key, []);
            return {
                ...state,
                data: {
                    ...state.data,
                    [payload.key]: mergeTrackerData(trackerData, payload.data),
                },
            };
        }
        default:
            return state;
    }
}

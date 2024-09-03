import { library } from "@fortawesome/fontawesome-svg-core";
import * as Icons from "@fortawesome/pro-duotone-svg-icons";
import Flexsearch from "flexsearch";
import _ from "lodash";
const iconList = Object.keys(Icons).filter(
    (key) => key !== "fad" && key !== "prefix"
);
library.add(...iconList.map((icon) => Icons[icon]));
const Index = Flexsearch.Index ?? Flexsearch;
const index = Index({ tokenize: "reverse" });
let store = {};
const wordRegex = /[A-Z]?[a-z]+|[0-9]+|[A-Z]+(?![a-z])/g;
let iconSearchTags = {};
for (let i = 0; i < _.size(iconList); i++) {
    const iconName = Icons[iconList[i]].iconName;
    const tags = iconList[i].slice(2).match(wordRegex);
    if (_.has(iconSearchTags, iconName)) {
        iconSearchTags[iconName] = iconSearchTags[iconName].concat(tags);
    } else {
        iconSearchTags[iconName] = tags;
    }
}
const searchTagKeys = Object.keys(iconSearchTags);
for (let i = 0; i < _.size(searchTagKeys); i++) {
    store[i] = searchTagKeys[i];
    index.add(i, _.join(iconSearchTags[searchTagKeys[i]], " "));
}
export const defaultState = {
    users: {},
    pendingRequests: {},
    iconPickerIndex: index,
    iconPickerStore: store,
    settings: {},
};
export default function appReducer(state = defaultState, { type, payload }) {
    let { pendingRequests } = state;
    switch (type) {
        case "app/pendingRequests/set": {
            _.set(pendingRequests, payload.key, payload.value);
            return { ...state, pendingRequests };
        }
        case "app/users/profile/add": {
            if (_.isEmpty(payload)) {
                return { ...state };
            } else {
                return {
                    ...state,
                    users: {
                        ...state.users,
                        [payload.uid]: payload,
                    },
                };
            }
        }
        default:
            return state;
    }
}

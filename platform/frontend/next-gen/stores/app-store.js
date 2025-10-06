import { library } from "@fortawesome/fontawesome-svg-core";
import * as Icons from "@fortawesome/sharp-duotone-solid-svg-icons";
import Flexsearch from "flexsearch";
import _ from "lodash";
import { create } from "zustand";
const icons = _.keys(Icons).filter(
    (key) => !_.isEqual(key, "fasds") && !_.isEqual(key, "prefix")
);
library.add(...icons.map((icon) => Icons[icon]));
const Index = Flexsearch.Index ?? Flexsearch;
const index = Index({ tokenize: "reverse" });
let store = {};
let searchTags = {};
for (let i = 0; i < _.size(icons); i++) {
    const name = Icons[icons[i]].iconName;
    const tags = icons[i]
        .slice(2)
        .match(/[A-Z]?[a-z]+|[0-9]+|[A-Z]+(?![a-z])/g);
    if (_.has(searchTags, name)) {
        searchTags[name] = searchTags[name].concat(tags);
    } else {
        searchTags[name] = tags;
    }
}
const searchTagKeys = _.keys(searchTags);
for (let i = 0; i < _.size(searchTagKeys); i++) {
    store[i] = searchTagKeys[i];
    index.add(i, _.join(searchTags[searchTagKeys[i]], " "));
}
export const useAppStore = create((set) => ({
    setState: ({ key, value }) => set({ [key]: value }),
    showOmnibar: false,
    iconIndex: index,
    iconStore: store,
    openOmnibar: () => {
        set({ showOmnibar: true });
    },
    closeOmnibar: () => {
        set({ showOmnibar: false });
    },
    omnibarItems: [],
}));

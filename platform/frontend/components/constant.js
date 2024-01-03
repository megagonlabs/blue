
module.exports = {
    DARK_THEME_CLASS: "bp4-dark",
    DARK_THEME_BACKGROUND_COLOR: "#353c46",
    LIGHT_THEME_CLASS: "",
    LIGHT_THEME_BACKGROUND_COLOR: "#f6f7f9",
    REQUIRED_INDICATOR: <span className="required">(required)</span>,
    DEBOUNCE_INTERVAL: 800,
    SHOW_MODE_MAP: {
        show_promoted: "Promoted",
        show_recent: "Recent",
        show_all: "All",
    },
    FILTER_PARAMETER_MAP: {
        graphIDs: {
            map: "graph",
        },
    },
    BUTTON_WITH_TOOLTIP2: { minimal: true},
    CRITERIA_OPTIONS: {
        GREATER_THAN: {
            icon: null,
            value: "GREATER_THAN",
        },
        GREATER_THAN_OR_EQUAL: {
            icon: null,
            value: "GREATER_THAN_OR_EQUAL",
        },
        LESS_THAN: {
            icon: null,
            value: "LESS_THAN",
        },
        LESS_THAN_OR_EQUAL: {
            icon: null,
            value: "LESS_THAN_OR_EQUAL",
        },
    },
    SHARE_STATES_MAP: {
        private: {
            icon: null,
            description: "Only you have access to view.",
        },
        organization: {
            icon: null,
            iconStyle: {
                color: "#2D72D2",
            },
            description: "Anyone in the organization can view.",
        },
        public: {
            icon: null,
            iconStyle: {
                color: "#238551",
            },
            description: "Anyone on the internet with the link can view.",
        },
    },
};
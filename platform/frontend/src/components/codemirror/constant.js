module.exports = {
    DATA_JSON_SCHEMA: {
        type: "object",
        definitions: {
            type: {
                type: "string",
                enum: ["object", "boolean", "integer", "number", "string"],
            },
            enum: { type: "array", minItems: 1 },
        },
        properties: {
            type: { $ref: "#/definitions/type" },
            enum: { $ref: "#/definitions/enum" },
        },
        patternProperties: {
            "^.*$": {
                properties: {
                    type: { $ref: "#/definitions/type" },
                    enum: { $ref: "#/definitions/enum" },
                },
                additionalProperties: { $ref: "#" },
            },
        },
    },
    UI_JSON_SCHEMA: {
        type: "object",
        required: ["type"],
        additionalProperties: false,
        properties: {
            type: {
                type: "string",
                enum: [
                    "VerticalLayout",
                    "HorizontalLayout",
                    "Button",
                    "Control",
                    "Label",
                    "Group",
                ],
            },
            label: { type: "string", minLength: 1 },
            props: {
                type: "object",
                properties: {
                    switch: { type: "boolean" },
                    outlined: { type: "boolean" },
                    intent: { type: "string" },
                    inline: { type: "boolean" },
                    helperText: { type: "string", minLength: 1 },
                    collapsible: { type: "boolean" },
                    defaultIsOpen: { type: "boolean" },
                    compact: { type: "boolean" },
                    muted: { type: "boolean" },
                    small: { type: "boolean" },
                    large: { type: "boolean" },
                    spaceEvenly: { type: "boolean" },
                    placeholder: { type: "string", minLength: 1 },
                    style: { type: "object" },
                    streamId: { type: "string", minLength: 1 },
                    nameId: { type: "string", minLength: 1 },
                },
                additionalProperties: false,
            },
            options: { type: "object" },
            scope: { type: "string", minLength: 1 },
            required: { type: "boolean" },
            elements: { type: "array", items: { $ref: "#" } },
        },
    },
};

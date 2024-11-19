const NO_VALIDATION_KEYS = ["vl-spec", "md-content"].map((e) => `^${e}$`);
const NO_VALIDATION_PATTERN = `^(?!${NO_VALIDATION_KEYS.join("|")}).*$`;
module.exports = {
    DATA_JSON_SCHEMA: {
        type: "object",
        definitions: {
            type: {
                type: "string",
                enum: [
                    "object",
                    "boolean",
                    "integer",
                    "number",
                    "string",
                    "array",
                ],
            },
            enum: {
                type: "array",
                minItems: 1,
                uniqueItems: true,
                items: { type: "string" },
            },
        },
        properties: {
            type: { $ref: "#/definitions/type" },
            enum: { $ref: "#/definitions/enum" },
        },
        patternProperties: {
            [NO_VALIDATION_PATTERN]: {
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
                    "Tabs",
                    "Vega",
                    "Markdown",
                    "Callout",
                    "Table",
                ],
            },
            label: { type: "string", minLength: 1 },
            tabs: {
                type: "array",
                items: { type: "string", minLength: 1 },
                minItems: 1,
            },
            columns: {
                type: "array",
                items: { type: "string", minLength: 1 },
                minItems: 1,
            },
            rowCells: {
                type: "array",
                items: { type: "object", minLength: 1 },
                minItems: 1,
            },
            props: {
                type: "object",
                properties: {
                    switch: { type: "boolean" },
                    outlined: { type: "boolean" },
                    intent: { type: "string" },
                    inline: { type: "boolean" },
                    bordered: { type: "boolean" },
                    striped: { type: "boolean" },
                    helperText: { type: "string", minLength: 1 },
                    collapsible: { type: "boolean" },
                    defaultIsOpen: { type: "boolean" },
                    compact: { type: "boolean" },
                    muted: { type: "boolean" },
                    vertical: { type: "boolean" },
                    small: { type: "boolean" },
                    large: { type: "boolean" },
                    spaceEvenly: { type: "boolean" },
                    placeholder: { type: "string", minLength: 1 },
                    style: { type: "object" },
                    streamId: { type: "string", minLength: 1 },
                    formId: { type: "string", minLength: 1 },
                    action: { type: "string", minLength: 1 },
                    visualization: { type: "boolean" },
                    spec: { type: "object" },
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

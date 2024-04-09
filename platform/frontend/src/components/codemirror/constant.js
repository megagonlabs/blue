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
    UI_JSON_SCHEMA: {},
};

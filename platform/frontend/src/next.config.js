const createNextPluginPreval = require("next-plugin-preval/config");
const withNextPluginPreval = createNextPluginPreval();
module.exports = withNextPluginPreval({
    reactStrictMode: true,
    transpilePackages: ["codemirror-json-schema", "json-schema-library"],
    images: {
        remotePatterns: [{ hostname: "lh3.googleusercontent.com" }],
    },
});

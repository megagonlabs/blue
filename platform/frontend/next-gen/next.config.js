const { configureRuntimeEnv } = require("next-runtime-env/build/configure");
configureRuntimeEnv();
module.exports = {
    reactStrictMode: true,
    transpilePackages: ["codemirror-json-schema", "json-schema-library"],
    images: { remotePatterns: [{ hostname: "lh3.googleusercontent.com" }] },
};

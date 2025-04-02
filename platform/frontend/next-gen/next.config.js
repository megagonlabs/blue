const { configureRuntimeEnv } = require("next-runtime-env/build/configure");
configureRuntimeEnv();
module.exports = {
    reactStrictMode: true,
    images: { remotePatterns: [{ hostname: "lh3.googleusercontent.com" }] },
};

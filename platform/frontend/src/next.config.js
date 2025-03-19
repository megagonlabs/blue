const { configureRuntimeEnv } = require("next-runtime-env/build/configure");
configureRuntimeEnv();
module.exports = {
    async rewrites() {
        return {
            beforeFiles: [
                {
                    source: `/registry/:l0agentRegistryName/:l1Type(agent|agent_group)/:path(.*\/agent)/:agentName/:l2Type(input|output)/new`,
                    destination: `/registry/:l0agentRegistryName/agent/:agentName/:l2Type/new`,
                },
                {
                    source: `/registry/:l0agentRegistryName/:l1Type(agent|agent_group)/:path(.*\/agent)/new`,
                    destination: `/registry/:l0agentRegistryName/agent/new`,
                },
            ],
        };
    },
    reactStrictMode: true,
    transpilePackages: ["codemirror-json-schema", "json-schema-library"],
    images: { remotePatterns: [{ hostname: "lh3.googleusercontent.com" }] },
};

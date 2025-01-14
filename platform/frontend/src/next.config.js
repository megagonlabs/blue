module.exports = {
    async rewrites() {
        const agentRegistryName = process.env.NEXT_PUBLIC_AGENT_REGISTRY_NAME;
        return [
            {
                source: `/registry/${agentRegistryName}/:l1Type(agent|agent_group)/:path(.*\/agent)/:agentName/:l2Type(input|output)/new`,
                destination: `/registry/${agentRegistryName}/agent/:agentName/:l2Type/new`,
            },
            {
                source: `/registry/${agentRegistryName}/:l1Type(agent|agent_group)/:path(.*\/agent)/new`,
                destination: `/registry/${agentRegistryName}/agent/new`,
            },
        ];
    },
    reactStrictMode: true,
    transpilePackages: ["codemirror-json-schema", "json-schema-library"],
    images: {
        remotePatterns: [{ hostname: "lh3.googleusercontent.com" }],
    },
};

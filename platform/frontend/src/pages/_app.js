import App from "@/components/App";
import { AppProvider } from "@/components/contexts/app-context";
import { AuthProvider } from "@/components/contexts/auth-context";
import { SocketProvider } from "@/components/contexts/socket-context";
import "@/styles/custom.css";
import "@/styles/docs.css";
import "@/styles/markdown-dark.css";
import "@/styles/markdown-light.css";
import { FocusStyleManager } from "@blueprintjs/core";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";
import "@blueprintjs/table/lib/css/table.css";
import "@xyflow/react/dist/style.css";
import "allotment/dist/style.css";
import axios from "axios";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import dynamic from "next/dynamic";
import Head from "next/head";
import "normalize.css/normalize.css";
TimeAgo.addDefaultLocale(en);
axios.defaults.withCredentials = true;
const { NEXT_PUBLIC_REST_API_SERVER, NEXT_PUBLIC_PLATFORM_NAME } = allEnv();
axios.defaults.baseURL = `${NEXT_PUBLIC_REST_API_SERVER}/blue/platform/${NEXT_PUBLIC_PLATFORM_NAME}`;
FocusStyleManager.onlyShowFocusOnTabs();
const Blue = ({ Component, pageProps }) => {
    if (_.isEqual(typeof window, "object"))
        return (
            <AppProvider>
                <Head>
                    <title>Blue &#91;{NEXT_PUBLIC_PLATFORM_NAME}&#93;</title>
                    <link rel="icon" href="/favicon.ico" />
                    <meta
                        name="viewport"
                        content="width=device-width, initial-scale=1.0"
                    />
                </Head>
                <style jsx global>{`
                    body {
                        overflow: hidden;
                    }
                `}</style>
                <AuthProvider>
                    <SocketProvider>
                        <App>
                            <Component {...pageProps} />
                        </App>
                    </SocketProvider>
                </AuthProvider>
            </AppProvider>
        );
    return null;
};
export default dynamic(() => Promise.resolve(Blue), { ssr: true });

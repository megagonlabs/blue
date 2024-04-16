import App from "@/components/App";
import { AppProvider } from "@/components/contexts/app-context";
import { AuthProvider } from "@/components/contexts/auth-context";
import { SocketProvider } from "@/components/contexts/websocket";
import "@/styles/custom.css";
import "@/styles/docs.css";
import { FocusStyleManager } from "@blueprintjs/core";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";
import "allotment/dist/style.css";
import axios from "axios";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en";
import _ from "lodash";
import dynamic from "next/dynamic";
import Head from "next/head";
import "normalize.css/normalize.css";
TimeAgo.addLocale(en);
axios.defaults.withCredentials = true;
axios.defaults.baseURL = process.env.NEXT_PUBLIC_REST_API_SERVER;
FocusStyleManager.onlyShowFocusOnTabs();
const Blue = ({ Component, pageProps }) => {
    if (_.isEqual(typeof window, "object"))
        return (
            <AppProvider>
                <Head>
                    <title>Blue</title>
                    <link rel="icon" href="/favicon.ico" />
                </Head>
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

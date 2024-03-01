import App from "@/components/App";
import { AppProvider } from "@/components/app-context";
import { FocusStyleManager } from "@blueprintjs/core";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";
import axios from "axios";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en";
import _ from "lodash";
import dynamic from "next/dynamic";
import Head from "next/head";
import "normalize.css/normalize.css";
import "../styles/custom.css";
TimeAgo.addLocale(en);
axios.defaults.withCredentials = true;
axios.defaults.baseURL = process.env.NEXT_PUBLIC_API_SERVER;
FocusStyleManager.onlyShowFocusOnTabs();
const Blue = ({ Component, pageProps }) => {
    if (_.isEqual(typeof window, "object"))
        return (
            <AppProvider>
                <Head>
                    <title>Blue</title>
                    <link rel="icon" href="/favicon.ico" />
                </Head>
                <App>
                    <Component {...pageProps} />
                </App>
            </AppProvider>
        );
    return null;
};
export default dynamic(() => Promise.resolve(Blue), { ssr: false });

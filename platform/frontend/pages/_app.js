import App from "@/components/app";
import { AppProvider } from "@/components/app-context";
import { FocusStyleManager } from "@blueprintjs/core";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";
import _ from "lodash";
import dynamic from "next/dynamic";
import Head from "next/head";
import "normalize.css/normalize.css";
FocusStyleManager.onlyShowFocusOnTabs();
const Blue = ({ Component, pageProps }) => {
    if (_.isEqual(typeof window, "object"))
        return (
            <AppProvider>
                <Head>
                    <title>Blue</title>
                    <link rel="icon" href="/images/favicon.ico" />
                </Head>
                <App>
                    <Component {...pageProps} />
                </App>
            </AppProvider>
        );
    return null;
};
export default dynamic(() => Promise.resolve(Blue), {
    ssr: false,
});

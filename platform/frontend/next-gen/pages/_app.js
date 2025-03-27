import Blue from "@/components/Blue";
import "@/styles/custom.css";
import "@/styles/global.css";
import { FocusStyleManager } from "@blueprintjs/core";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";
import "@blueprintjs/select/lib/css/blueprint-select.css";
import _ from "lodash";
import dynamic from "next/dynamic";
import Head from "next/head";
import "normalize.css/normalize.css";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
FocusStyleManager.onlyShowFocusOnTabs();

const App = ({ Component, pageProps }) => {
    if (_.isEqual(typeof window, "object")) {
        return (
            <Blue>
                <Head>
                    <title>Blue</title>
                    <link rel="icon" href="/favicon.ico" />
                    <meta
                        name="viewport"
                        content="width=device-width, initial-scale=1.0"
                    />
                </Head>
                <Component {...pageProps} />
            </Blue>
        );
    }
    return null;
};
export default dynamic(() => Promise.resolve(App), { ssr: true });

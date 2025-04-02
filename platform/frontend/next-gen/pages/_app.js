import AuthErrorHandler from "@/components/AuthErrorHandler";
import Blue from "@/components/Blue";
import "@/styles/custom.css";
import "@/styles/global.css";
import { FocusStyleManager } from "@blueprintjs/core";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";
import "@blueprintjs/select/lib/css/blueprint-select.css";
import axios from "axios";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import dynamic from "next/dynamic";
import Head from "next/head";
import "normalize.css/normalize.css";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
FocusStyleManager.onlyShowFocusOnTabs();
const { NEXT_PUBLIC_REST_API_SERVER, NEXT_PUBLIC_PLATFORM_NAME } = allEnv();
axios.defaults.baseURL = `${NEXT_PUBLIC_REST_API_SERVER}/blue/platform/${NEXT_PUBLIC_PLATFORM_NAME}`;
axios.defaults.withCredentials = true;

const App = ({ Component, pageProps }) => {
    if (_.isEqual(typeof window, "object")) {
        return (
            <AuthErrorHandler>
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
            </AuthErrorHandler>
        );
    }
    return null;
};
export default dynamic(() => Promise.resolve(App), { ssr: true });

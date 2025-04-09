import AuthErrorHandler from "@/components/AuthErrorHandler";
import Blue from "@/components/Blue";
import SocketHandler from "@/components/SocketHandler";
import "@/styles/custom.css";
import "@/styles/docs.css";
import "@/styles/global.css";
import { FocusStyleManager } from "@blueprintjs/core";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";
import "@blueprintjs/select/lib/css/blueprint-select.css";
import { library } from "@fortawesome/fontawesome-svg-core";
import * as Icons from "@fortawesome/sharp-duotone-solid-svg-icons";
import "allotment/dist/style.css";
import axios from "axios";
import { ElementQueries } from "css-element-queries";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import dynamic from "next/dynamic";
import Head from "next/head";
import "normalize.css/normalize.css";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
FocusStyleManager.onlyShowFocusOnTabs();
if (typeof window !== "undefined") ElementQueries.listen();
const { NEXT_PUBLIC_REST_API_SERVER, NEXT_PUBLIC_PLATFORM_NAME } = allEnv();
axios.defaults.baseURL = `${NEXT_PUBLIC_REST_API_SERVER}/blue/platform/${NEXT_PUBLIC_PLATFORM_NAME}`;
axios.defaults.withCredentials = true;
const iconList = _.keys(Icons).filter(
    (key) => !_.isEqual(key, "fasds") && !_.isEqual(key, "prefix")
);
library.add(...iconList.map((icon) => Icons[icon]));
const App = ({ Component, pageProps }) => {
    if (_.isEqual(typeof window, "object")) {
        return (
            <AuthErrorHandler>
                <SocketHandler>
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
                </SocketHandler>
            </AuthErrorHandler>
        );
    }
    return null;
};
export default dynamic(() => Promise.resolve(App), { ssr: true });

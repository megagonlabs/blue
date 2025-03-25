import Blue from "@/components/Blue";
import "@/styles/custom.css";
import { FocusStyleManager } from "@blueprintjs/core";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@blueprintjs/icons/lib/css/blueprint-icons.css";
import _ from "lodash";
import dynamic from "next/dynamic";
import "normalize.css/normalize.css";
FocusStyleManager.onlyShowFocusOnTabs();

const App = ({ Component, pageProps }) => {
    if (_.isEqual(typeof window, "object")) {
        return (
            <Blue>
                <Component {...pageProps} />
            </Blue>
        );
    }
    return null;
};
export default dynamic(() => Promise.resolve(App), { ssr: true });

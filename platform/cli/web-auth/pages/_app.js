import "@/public/custom.css";
import { FocusStyleManager } from "@blueprintjs/core";
import "@blueprintjs/core/lib/css/blueprint.css";
import "@fortawesome/fontawesome-svg-core/styles.css";
import _ from "lodash";
import "normalize.css/normalize.css";
FocusStyleManager.onlyShowFocusOnTabs();
export default function App({ Component, pageProps }) {
    if (_.isEqual(typeof window, "object")) return <Component {...pageProps} />;
    return null;
}

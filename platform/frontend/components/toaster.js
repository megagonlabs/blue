import { OverlayToaster, Position } from "@blueprintjs/core";
import _ from "lodash";
export const actionToaster =
    typeof window !== "undefined"
        ? OverlayToaster.create({
              position: Position.BOTTOM,
          })
        : null;
export const createToast = (toast, theme = "") => ({
    className: theme,
    icon: null,
    action: toast.action,
    intent: toast.intent,
    message: toast.message,
    timeout: _.isUndefined(toast.timeout) ? 5000 : toast.timeout,
});

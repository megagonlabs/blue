import { OverlayToaster, Position } from "@blueprintjs/core";
export const AppToaster =
    typeof window !== "undefined"
        ? OverlayToaster.create({
              position: Position.BOTTOM,
          })
        : null;

export const actionToaster =
    typeof window !== "undefined"
        ? OverlayToaster.create({
                position: Position.BOTTOM_RIGHT,
            })
        : null;
export const createToast = (toast) => ({
    icon: _.isNil(toast.icon) ? null : <Icon icon="help" />,
    action: toast.action,
    intent: toast.intent,
    message: toast.message,
    timeout: _.isUndefined(toast.timeout) ? 5000 : toast.timeout,
});

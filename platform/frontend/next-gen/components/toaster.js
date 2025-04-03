import { OverlayToaster, Position } from "@blueprintjs/core";
export const AppToaster =
    typeof window !== "undefined"
        ? OverlayToaster.create({
              position: Position.BOTTOM,
          })
        : null;
export const ProgressToaster =
    typeof window !== "undefined"
        ? OverlayToaster.create({
              position: Position.TOP,
          })
        : null;

import { OverlayToaster, Position } from "@blueprintjs/core";
export const AppToaster =
    typeof window !== "undefined"
        ? OverlayToaster.create({
              position: Position.BOTTOM,
          })
        : null;

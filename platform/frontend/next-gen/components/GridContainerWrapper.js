import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useEffect } from "react";
import { useGridContainerContext } from "./contexts/GridContainerContext";
export default function GridContainerWrapper({ children, gridRef }) {
    const { gridContainerId } = useGridContainerContext();
    const fullWindowHeight = useAppStore((state) => state.full_window_height);
    const resizeContainerHeight = useGridStore(
        (state) => state.resizeContainerHeight
    );
    useEffect(() => {
        if (fullWindowHeight) {
            resizeContainerHeight({ id: gridContainerId, grid: gridRef });
        }
    }, []);
    return children;
}

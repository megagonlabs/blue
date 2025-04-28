import { ContainerContextProvider } from "@/components/contexts/ContainerContext";
import { FAIcon } from "@/components/FAIcon";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Button,
    ButtonVariant,
    Classes,
    Intent,
    Size,
} from "@blueprintjs/core";
import { faXmark } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { forwardRef } from "react";
import RGL, { WidthProvider } from "react-grid-layout";
import { useShallow } from "zustand/react/shallow";
const ReactGridLayout = WidthProvider(RGL);
const CustomResizeHandle = forwardRef(
    ({ handleAxis, className, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={`react-resizable-handle react-resizable-handle-${handleAxis} z-index-21`}
                {...props}
            />
        );
    }
);
export default function Home() {
    const { layout, setLayout, containers, removeContainer } = useGridStore(
        useShallow((state) => ({
            layout: state.layout,
            setLayout: state.setLayout,
            containers: state.containers,
            removeContainer: state.removeContainer,
        }))
    );
    return (
        <div className="full-parent-dimension" style={{ overflowY: "auto" }}>
            <ReactGridLayout
                resizeHandle={(handleAxis, ref) => (
                    <CustomResizeHandle ref={ref} handleAxis={handleAxis} />
                )}
                draggableHandle=".react-grid-drag-handle"
                layout={layout}
                resizeHandles={["sw", "nw", "se", "ne"]}
                margin={[20, 20]}
                containerPadding={[20, 20]}
                onLayoutChange={(layout) => setLayout(layout)}
            >
                {layout.map((element) => (
                    <div
                        key={element.i}
                        className="padding-0 overflow-hidden border-radius-10 custom-card"
                        style={{ zIndex: 3 }}
                    >
                        <div
                            className="border-bottom"
                            style={{
                                padding: "10px 20px",
                                display: "flex",
                                alignItems: "center",
                                gap: 10,
                            }}
                        >
                            <Button
                                intent={Intent.DANGER}
                                size={Size.SMALL}
                                variant={ButtonVariant.MINIMAL}
                                icon={<FAIcon icon={faXmark} />}
                                onClick={() => removeContainer(element.i)}
                            />
                            <div
                                className={classNames(
                                    "react-grid-drag-handle",
                                    "user-selection-none",
                                    Classes.TEXT_LARGE,
                                    Classes.TEXT_OVERFLOW_ELLIPSIS
                                )}
                                style={{
                                    width: "calc(100% - 24px)",
                                    fontWeight: 600,
                                }}
                            >
                                {_.get(containers, [element.i, "title"], null)}
                            </div>
                        </div>
                        <div
                            className="overflow-hidden grid-container-boundary"
                            style={{ height: "calc(100% - 45px)" }}
                        >
                            <ContainerContextProvider
                                value={{ containerId: element.i }}
                            >
                                {_.get(
                                    containers,
                                    [element.i, "content"],
                                    null
                                )}
                            </ContainerContextProvider>
                        </div>
                    </div>
                ))}
            </ReactGridLayout>
        </div>
    );
}

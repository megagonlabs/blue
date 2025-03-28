import { FAIcon } from "@/components/FAIcon";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Button,
    ButtonVariant,
    Card,
    Classes,
    Intent,
    Size,
} from "@blueprintjs/core";
import { faXmark } from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import RGL, { WidthProvider } from "react-grid-layout";
const ReactGridLayout = WidthProvider(RGL);

export default function Home() {
    const layout = useGridStore((state) => state.layout);
    const setLayout = useGridStore((state) => state.setLayout);
    const containers = useGridStore((state) => state.containers);
    const removeContainer = useGridStore((state) => state.removeContainer);
    return (
        <div className="full-parent-dimension" style={{ overflowY: "auto" }}>
            <ReactGridLayout
                draggableHandle=".react-grid-drag-handle"
                layout={layout}
                resizeHandles={["sw", "nw", "se", "ne"]}
                margin={[20, 20]}
                containerPadding={[20, 20]}
                onLayoutChange={(layout) => setLayout(layout)}
            >
                {layout.map((element) => (
                    <Card
                        key={element.i}
                        className="padding-0 overflow-hidden"
                        style={{ zIndex: 3 }}
                    >
                        <div
                            className="border-bottom"
                            style={{
                                padding: "0px 20px",
                                fontWeight: 600,
                                display: "flex",
                                alignItems: "center",
                                gap: 20,
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
                                    Classes.TEXT_OVERFLOW_ELLIPSIS
                                )}
                                style={{
                                    width: "calc(100% - 24px)",
                                    lineHeight: "44px",
                                }}
                            >
                                {_.get(containers, [element.i, "title"], null)}
                            </div>
                        </div>
                        <div
                            className="overflow-hidden"
                            style={{ height: "calc(100% - 34px)" }}
                        >
                            {_.get(containers, [element.i, "content"], null)}
                        </div>
                    </Card>
                ))}
            </ReactGridLayout>
        </div>
    );
}

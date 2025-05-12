import { ContainerContextProvider } from "@/components/contexts/ContainerContext";
import { FAIcon } from "@/components/FAIcon";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Classes,
    Colors,
    Divider,
    Intent,
    Menu,
    MenuDivider,
    MenuItem,
    Popover,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import {
    faExpand,
    faXmarkLarge,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
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
    const {
        layout,
        setLayout,
        containers,
        removeContainer,
        resizeContainerWidth,
    } = useGridStore(
        useShallow((state) => ({
            layout: state.layout,
            setLayout: state.setLayout,
            containers: state.containers,
            removeContainer: state.removeContainer,
            resizeContainerWidth: state.resizeContainerWidth,
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
                        className="grid-container-boundary padding-0 overflow-hidden border-radius-10 custom-card"
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
                            <ButtonGroup
                                style={{ marginRight: 10 }}
                                variant={ButtonVariant.MINIMAL}
                                size={Size.SMALL}
                            >
                                <Button
                                    intent={Intent.DANGER}
                                    icon={<FAIcon icon={faXmarkLarge} />}
                                    onClick={() => {
                                        removeContainer(element.i);
                                    }}
                                />
                                <Divider className="visibility-hidden" />
                                <Popover
                                    placement="bottom"
                                    modifiers={{
                                        offset: {
                                            enabled: true,
                                            options: { offset: [40, 14] },
                                        },
                                    }}
                                    content={
                                        <Menu>
                                            <MenuDivider title="Resize" />
                                            <MenuItem
                                                text="5"
                                                labelElement="42%"
                                                onClick={() => {
                                                    resizeContainerWidth({
                                                        id: element.i,
                                                        width: 5,
                                                    });
                                                }}
                                            />
                                            <MenuItem
                                                text="6"
                                                labelElement="50%"
                                                onClick={() => {
                                                    resizeContainerWidth({
                                                        id: element.i,
                                                        width: 6,
                                                    });
                                                }}
                                            />
                                            <MenuItem
                                                text="7"
                                                labelElement="58%"
                                                onClick={() => {
                                                    resizeContainerWidth({
                                                        id: element.i,
                                                        width: 7,
                                                    });
                                                }}
                                            />
                                            <MenuItem
                                                text="12"
                                                labelElement="Full Width"
                                                onClick={() => {
                                                    resizeContainerWidth({
                                                        id: element.i,
                                                        width: 12,
                                                    });
                                                }}
                                            />
                                        </Menu>
                                    }
                                >
                                    <Tooltip
                                        content="Resize"
                                        placement="bottom"
                                    >
                                        <Button
                                            intent={Intent.SUCCESS}
                                            icon={<FAIcon icon={faExpand} />}
                                        />
                                    </Tooltip>
                                </Popover>
                            </ButtonGroup>
                            <div
                                className="react-grid-drag-handle user-selection-none"
                                style={{
                                    width: "calc(100% - 79px)",
                                    fontWeight: 600,
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                }}
                            >
                                <div
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                    }}
                                    className={classNames(
                                        Classes.TEXT_OVERFLOW_ELLIPSIS,
                                        Classes.TEXT_LARGE
                                    )}
                                >
                                    <FAIcon
                                        style={{
                                            marginRight: 10,
                                            color: Colors.GRAY1,
                                        }}
                                        icon={_.get(
                                            containers,
                                            [element.i, "icon"],
                                            null
                                        )}
                                    />
                                    {_.get(
                                        containers,
                                        [element.i, "title"],
                                        null
                                    )}
                                </div>
                            </div>
                        </div>
                        <div
                            className="overflow-hidden"
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

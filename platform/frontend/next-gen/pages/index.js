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
    FormGroup,
    Intent,
    Popover,
    PopoverInteractionKind,
    Size,
} from "@blueprintjs/core";
import {
    faExpand,
    faXmarkLarge,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { forwardRef, useRef } from "react";
import RGL, { WidthProvider } from "react-grid-layout";
import { useShallow } from "zustand/react/shallow";
const ReactGridLayout = WidthProvider(RGL);
const CustomResizeHandle = forwardRef(function CustomResizeHandle(
    { handleAxis, ...props },
    ref
) {
    return (
        <div
            {...props}
            ref={ref}
            className={`react-resizable-handle react-resizable-handle-${handleAxis} z-index-21`}
        />
    );
});
const WIDTH_ADJUSTMENT_BUTTONS = [
    { width: 5, text: "40" },
    { width: 6, text: "50" },
    { width: 7, text: "60" },
    { width: 12, text: "100" },
];
export default function Home() {
    const {
        layout,
        setLayout,
        containers,
        removeContainer,
        resizeContainerWidth,
        resizeContainerFullHeight,
    } = useGridStore(
        useShallow((state) => ({
            layout: state.layout,
            setLayout: state.setLayout,
            containers: state.containers,
            removeContainer: state.removeContainer,
            resizeContainerWidth: state.resizeContainerWidth,
            resizeContainerFullHeight: state.resizeContainerFullHeight,
        }))
    );
    const gridRef = useRef();
    return (
        <div
            ref={gridRef}
            className="full-parent-dimension"
            style={{ overflowY: "auto" }}
        >
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
                                padding: "0px 20px",
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
                                    interactionKind={
                                        PopoverInteractionKind.HOVER
                                    }
                                    modifiers={{
                                        offset: {
                                            enabled: true,
                                            options: { offset: [31, 14] },
                                        },
                                    }}
                                    content={
                                        <div style={{ padding: 10 }}>
                                            <FormGroup label="Width">
                                                <ButtonGroup
                                                    fill
                                                    variant={
                                                        ButtonVariant.MINIMAL
                                                    }
                                                >
                                                    {WIDTH_ADJUSTMENT_BUTTONS.map(
                                                        (spec) => (
                                                            <Button
                                                                key={spec.text}
                                                                intent={
                                                                    Intent.PRIMARY
                                                                }
                                                                onClick={() => {
                                                                    resizeContainerWidth(
                                                                        {
                                                                            id: element.i,
                                                                            width: spec.width,
                                                                        }
                                                                    );
                                                                }}
                                                                text={spec.text}
                                                            />
                                                        )
                                                    )}
                                                </ButtonGroup>
                                            </FormGroup>
                                            <FormGroup
                                                className="margin-0"
                                                label="Height"
                                            >
                                                <Button
                                                    variant={
                                                        ButtonVariant.MINIMAL
                                                    }
                                                    fill
                                                    text="Full height"
                                                    intent={Intent.PRIMARY}
                                                    onClick={() => {
                                                        resizeContainerFullHeight(
                                                            {
                                                                id: element.i,
                                                                grid: gridRef,
                                                            }
                                                        );
                                                    }}
                                                />
                                            </FormGroup>
                                        </div>
                                    }
                                >
                                    <Button
                                        intent={Intent.SUCCESS}
                                        icon={<FAIcon icon={faExpand} />}
                                    />
                                </Popover>
                            </ButtonGroup>
                            <div
                                className="react-grid-drag-handle user-selection-none"
                                style={{
                                    width: "calc(100% - 79px)",
                                    fontWeight: 600,
                                    display: "flex",
                                    height: 44,
                                    paddingRight: 79,
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

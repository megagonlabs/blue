import { scrollToTarget } from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Card,
    Colors,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { faQuestion } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "./FAIcon";
import VerticalScrollable from "./VerticalScrollable";
export default function Dock() {
    const darkMode = useAppStore((state) => state.dark_mode);
    const { layout, containers } = useGridStore(
        useShallow((state) => ({
            layout: state.layout,
            containers: state.containers,
        }))
    );
    const sortedLayout = _.sortBy(layout, ["y", "x"]);
    if (_.isEmpty(sortedLayout)) {
        return null;
    }
    return (
        <Card
            className="border-radius-10"
            style={{
                position: "absolute",
                padding: 10,
                top: 105,
                left: 20,
                width: 65,
                height: Math.min(400, 40 * _.size(sortedLayout)) + 50,
                maxHeight: "calc(100% - 210px)",
                overflow: "hidden",
            }}
        >
            <Tag style={{ textAlign: "center", marginBottom: 10 }} minimal fill>
                Dock
            </Tag>
            <div style={{ height: "calc(100% - 30px)" }}>
                <VerticalScrollable
                    backgroundColor={
                        darkMode ? Colors.DARK_GRAY2 : Colors.WHITE
                    }
                >
                    <ButtonGroup
                        vertical
                        size={Size.LARGE}
                        variant={ButtonVariant.MINIMAL}
                        fill
                    >
                        {sortedLayout.map((element) => (
                            <Tooltip
                                placement="right"
                                content={_.get(
                                    containers,
                                    [element.i, "title"],
                                    "-"
                                )}
                            >
                                <Button
                                    style={{ width: 65 }}
                                    onClick={() => {
                                        const containerId =
                                            "react-grid-scrollable-container";
                                        const targetId = `grid-container-${element.i}`;
                                        scrollToTarget(containerId, targetId);
                                    }}
                                    icon={
                                        <FAIcon
                                            icon={_.get(
                                                containers,
                                                [element.i, "icon"],
                                                faQuestion
                                            )}
                                        />
                                    }
                                    key={element.i}
                                />
                            </Tooltip>
                        ))}
                    </ButtonGroup>
                </VerticalScrollable>
            </div>
        </Card>
    );
}

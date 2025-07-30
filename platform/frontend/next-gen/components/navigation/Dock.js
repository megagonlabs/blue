import { FAIcon } from "@/components/FAIcon";
import { scrollToTarget } from "@/components/helper";
import VerticalScrollable from "@/components/VerticalScrollable";
import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Colors,
    Intent,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { faQuestion } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useShallow } from "zustand/react/shallow";
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
        <div
            className="full-parent-width border-bottom"
            style={{
                height: Math.min(400, 40 * _.size(sortedLayout)) + 41,
                overflow: "hidden",
                position: "relative",
                padding: "10px 0px",
                marginBottom: 20,
            }}
        >
            <Tag
                minimal
                intent={Intent.PRIMARY}
                style={{
                    top: 0,
                    left: 0,
                    width: 65,
                    position: "absolute",
                    textAlign: "center",
                }}
                fill
            >
                Dock
            </Tag>
            <div style={{ height: "calc(100% - 20px)", marginTop: 20 }}>
                <VerticalScrollable
                    backgroundColor={
                        darkMode ? Colors.DARK_GRAY1 : Colors.LIGHT_GRAY5
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
                                key={element.i}
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
        </div>
    );
}

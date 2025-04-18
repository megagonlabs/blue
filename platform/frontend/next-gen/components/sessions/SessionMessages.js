import { useSessionStore } from "@/stores/session-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Intent,
    Popover,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import { faBarsFilter } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useEffect, useRef } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../FAIcon";
const Row = ({ index, data, style }) => {};
export default function SessionMessages({ sessionId }) {
    const variableSizeListRef = useRef();
    const rowRef = useRef({});
    const rowHeights = useRef({});
    function setRowHeight(index, size) {
        rowHeights.current = { ...rowHeights.current, [index]: size };
        if (variableSizeListRef.current) {
            variableSizeListRef.current.resetAfterIndex(0);
        }
    }
    const { messages, streams } = useSessionStore(
        useShallow((state) => ({
            messages: _.get(state, ["sessions", sessionId, "messages"], []),
            streams: _.get(state, ["sessions", sessionId, "streams"], {}),
        }))
    );
    function getRowHeight(index) {
        // 53: 1 line message height
        // 20: gap space between messages
        // 25: message metadata height
        let height = 53 + 20;
        return rowHeights.current[index] || height;
    }
    useEffect(() => {
        setTimeout(() => {
            requestAnimationFrame(() => {
                if (variableSizeListRef.current) {
                    variableSizeListRef.current.scrollToItem(
                        messages.length,
                        "end"
                    );
                }
            });
        }, 0);
    }, [variableSizeListRef]);
    return (
        <>
            <div className="border-bottom" style={{ padding: 10 }}>
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    <Popover>
                        <Tooltip
                            openOnTargetFocus={false}
                            minimal
                            placement="bottom-start"
                            content="Filter"
                        >
                            <Button
                                intent={Intent.PRIMARY}
                                alignText={Alignment.START}
                                icon={<FAIcon icon={faBarsFilter} />}
                                text={_.size()}
                            />
                        </Tooltip>
                    </Popover>
                </ButtonGroup>
            </div>
            <AutoSizer>
                {({ width, height }) => (
                    <VariableSizeList
                        itemData={{ setRowHeight }}
                        itemSize={getRowHeight}
                        itemCount={_.size(messages)}
                        width={width}
                        height={height - 61}
                        ref={variableSizeListRef}
                    >
                        {Row}
                    </VariableSizeList>
                )}
            </AutoSizer>
        </>
    );
}

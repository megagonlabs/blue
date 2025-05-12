import { MIN_ALLOTMENT_PANE_SIZE } from "@/components/constants";
import withAutoSizer from "@/components/hocs/withAutoSizer";
import Timestamp from "@/components/Timestamp";
import { useAppStore } from "@/stores/app-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Alignment,
    Classes,
    Colors,
    HTMLTable,
    Intent,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { Allotment } from "allotment";
import classNames from "classnames";
import _ from "lodash";
import { useRef, useState } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { useShallow } from "zustand/react/shallow";
import MessageViewer from "./MessageViewer";
function DebuggerContainer({ width, height, sessionId }) {
    const { session } = useSessionStore(
        useShallow((state) => ({
            session: _.get(state, ["sessions", sessionId], {}),
        }))
    );
    const { messages } = session;
    const darkMode = useAppStore((state) => state.dark_mode);
    const elementRef = useRef(null);
    const popoverBoundary =
        elementRef.current &&
        elementRef.current.closest(".grid-container-boundary");
    const [focusIndex, setFocusIndex] = useState(null);
    const CELL_CONTENT_STYLES = {
        height: 22,
        display: "flex",
        alignItems: "center",
    };
    return (
        <div
            ref={elementRef}
            style={{
                width,
                height,
                backgroundColor: darkMode ? Colors.BLACK : null,
            }}
        >
            <Allotment>
                <Allotment.Pane minSize={MIN_ALLOTMENT_PANE_SIZE}>
                    <div
                        className="full-parent-dimension"
                        style={{ overflowY: "auto" }}
                    >
                        <AutoSizer>
                            {({ width: tableWidth }) => (
                                <HTMLTable
                                    interactive
                                    striped
                                    className="table-header-sticky"
                                >
                                    <thead
                                        style={{
                                            position: "sticky",
                                            top: 0,
                                            backgroundColor: darkMode
                                                ? Colors.BLACK
                                                : Colors.WHITE,
                                            zIndex: 1,
                                        }}
                                    >
                                        <tr>
                                            <th className="border-bottom">
                                                <div style={{ paddingLeft: 9 }}>
                                                    Type
                                                </div>
                                            </th>
                                            <th className="border-bottom">
                                                Stream
                                            </th>
                                            <th
                                                className="border-bottom"
                                                style={{
                                                    textAlign: Alignment.END,
                                                }}
                                            >
                                                <div
                                                    style={{ paddingRight: 9 }}
                                                >
                                                    Time
                                                </div>
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody style={{ overflowY: "auto" }}>
                                        {messages.map((message, index) => (
                                            <tr
                                                onClick={() => {
                                                    setFocusIndex(index);
                                                }}
                                            >
                                                <td>
                                                    <div
                                                        style={{
                                                            ...CELL_CONTENT_STYLES,
                                                            width: 80,
                                                            paddingLeft: 9,
                                                        }}
                                                    >
                                                        <Tag
                                                            minimal
                                                            intent={
                                                                Intent.PRIMARY
                                                            }
                                                        >
                                                            {
                                                                message.contentType
                                                            }
                                                        </Tag>
                                                    </div>
                                                </td>
                                                <td>
                                                    <Tooltip
                                                        placement="bottom"
                                                        boundary={
                                                            popoverBoundary
                                                        }
                                                        content={
                                                            <div
                                                                style={{
                                                                    width: 300,
                                                                    wordBreak:
                                                                        "break-all",
                                                                }}
                                                            >
                                                                {message.stream}
                                                            </div>
                                                        }
                                                    >
                                                        <div
                                                            className={classNames(
                                                                "full-parent-width",
                                                                Classes.TEXT_OVERFLOW_ELLIPSIS
                                                            )}
                                                            style={{
                                                                lineHeight:
                                                                    "22px",
                                                                width: `${
                                                                    tableWidth -
                                                                    66 -
                                                                    180
                                                                }px`,
                                                            }}
                                                        >
                                                            {message.stream}
                                                        </div>
                                                    </Tooltip>
                                                </td>
                                                <td>
                                                    <div
                                                        style={{
                                                            ...CELL_CONTENT_STYLES,
                                                            width: 100,
                                                            paddingRight: 9,
                                                            justifyContent:
                                                                "end",
                                                            textAlign:
                                                                Alignment.END,
                                                        }}
                                                    >
                                                        <Timestamp
                                                            boundary={
                                                                popoverBoundary
                                                            }
                                                            placement="bottom"
                                                            date={
                                                                message.timestamp
                                                            }
                                                        />
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </HTMLTable>
                            )}
                        </AutoSizer>
                    </div>
                </Allotment.Pane>
                <Allotment.Pane minSize={MIN_ALLOTMENT_PANE_SIZE}>
                    {_.isInteger(focusIndex) &&
                        focusIndex >= 0 &&
                        focusIndex < _.size(messages) && (
                            <MessageViewer
                                sessionId={sessionId}
                                message={messages[focusIndex]}
                            />
                        )}
                </Allotment.Pane>
            </Allotment>
        </div>
    );
}
export default withAutoSizer(DebuggerContainer);

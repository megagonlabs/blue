import { POPOVER_CONTENT_MAX_WIDTH } from "@/components/constants";
import { FAIcon } from "@/components/FAIcon";
import Timestamp from "@/components/Timestamp";
import {
    Alignment,
    Button,
    ButtonVariant,
    Classes,
    H5,
    HTMLTable,
    Intent,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faSquareExclamation,
    faSquareTerminal,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { faAngleDown, faAngleRight } from "@fortawesome/sharp-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useRef, useState } from "react";
export default function Error({ content }) {
    const type = _.get(content, "type", "Unknown BlueError");
    const intent = _.get(content, "intent", "fatal");
    const log = _.get(content, "log", []);
    const stackTrace = _.get(content, "stack_trace", []);
    const [showStackTrace, setShowStackTrace] = useState(false);
    const elementRef = useRef(null);
    return (
        <div ref={elementRef}>
            <HTMLTable compact striped className="full-parent-width">
                <thead>
                    <tr>
                        <th
                            className="padding-top-0 padding-left-0 padding-right-0"
                            colSpan={2}
                        >
                            <Button
                                intent={Intent.DANGER}
                                className="pointer-events-none"
                                alignText={Alignment.START}
                                variant={ButtonVariant.MINIMAL}
                            >
                                <div
                                    style={{
                                        display: "flex",
                                        gap: 10,
                                        alignItems: "center",
                                    }}
                                >
                                    <Tag
                                        className="padding-0"
                                        minimal
                                        intent={Intent.DANGER}
                                        style={{
                                            backgroundColor: "transparent",
                                            fontWeight: 600,
                                        }}
                                        size={Size.LARGE}
                                        icon={
                                            <FAIcon
                                                size={20}
                                                icon={faSquareExclamation}
                                                style={{ marginRight: 10 }}
                                            />
                                        }
                                    >
                                        <H5 className="margin-0">{type}</H5>
                                    </Tag>
                                    <Tag intent={Intent.DANGER}>{intent}</Tag>
                                </div>
                            </Button>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {log.map((element, index) => (
                        <tr key={index}>
                            <td style={{ minWidth: 130 }}>
                                <Timestamp epoch={element.timestamp} />
                            </td>
                            <td>
                                {element.description}
                                <Tag
                                    minimal
                                    intent={Intent.PRIMARY}
                                    style={{ marginLeft: 5 }}
                                >
                                    {element.caller}
                                </Tag>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </HTMLTable>
            <HTMLTable
                compact
                bordered
                className="full-parent-width"
                style={{ tableLayout: "fixed", marginTop: 20 }}
            >
                <thead>
                    <tr>
                        <th className="padding-top-0 padding-left-0 padding-right-0">
                            <Button
                                disabled={_.isEmpty(stackTrace)}
                                alignText={Alignment.START}
                                variant={ButtonVariant.MINIMAL}
                                fill
                                onClick={() =>
                                    setShowStackTrace(!showStackTrace)
                                }
                                endIcon={
                                    <FAIcon
                                        icon={
                                            showStackTrace
                                                ? faAngleDown
                                                : faAngleRight
                                        }
                                    />
                                }
                            >
                                <div
                                    style={{
                                        display: "flex",
                                        gap: 10,
                                        alignItems: "center",
                                    }}
                                >
                                    <Tag
                                        className="padding-0"
                                        minimal
                                        style={{
                                            backgroundColor: "transparent",
                                            fontWeight: 600,
                                        }}
                                        size={Size.LARGE}
                                        icon={
                                            <FAIcon
                                                size={20}
                                                icon={faSquareTerminal}
                                                style={{ marginRight: 10 }}
                                            />
                                        }
                                    >
                                        Stack Trace
                                    </Tag>
                                    <Tag round>{_.size(stackTrace)}</Tag>
                                </div>
                            </Button>
                        </th>
                    </tr>
                </thead>
                {showStackTrace && (
                    <tbody>
                        {stackTrace.map((element, index) => (
                            <tr key={index}>
                                <td>
                                    <div
                                        className="split-pane-container"
                                        style={{ rowGap: 0 }}
                                    >
                                        <div
                                            className={classNames(
                                                ".pane-item",
                                                Classes.TEXT_OVERFLOW_ELLIPSIS
                                            )}
                                            style={{
                                                display: "flex",
                                                alignItems: "center",
                                                gap: 5,
                                            }}
                                        >
                                            <Tag
                                                className="padding-0"
                                                size={Size.LARGE}
                                                minimal
                                                intent={Intent.PRIMARY}
                                                style={{
                                                    fontWeight: 600,
                                                    backgroundColor:
                                                        "transparent",
                                                }}
                                            >
                                                {element.function}
                                            </Tag>
                                            <div
                                                className={classNames(
                                                    Classes.TEXT_DISABLED,
                                                    "white-space-no-wrap"
                                                )}
                                            >
                                                in
                                            </div>
                                            <Tooltip
                                                placement="bottom"
                                                boundary={elementRef.current}
                                                content={
                                                    <div
                                                        style={{
                                                            maxWidth:
                                                                POPOVER_CONTENT_MAX_WIDTH,
                                                            wordBreak:
                                                                "break-all",
                                                        }}
                                                    >
                                                        {element.file}
                                                    </div>
                                                }
                                            >
                                                <div
                                                    className={classNames(
                                                        Classes.TEXT_MUTED,
                                                        "white-space-no-wrap"
                                                    )}
                                                >
                                                    {element.file
                                                        .split("/")
                                                        .pop()}
                                                </div>
                                            </Tooltip>
                                        </div>
                                        <div
                                            className={classNames(
                                                ".pane-item",
                                                Classes.TEXT_OVERFLOW_ELLIPSIS
                                            )}
                                            style={{
                                                display: "flex",
                                                alignItems: "center",
                                                gap: 5,
                                            }}
                                        >
                                            <Tag
                                                minimal
                                                style={{
                                                    minWidth: "fit-content",
                                                }}
                                            >
                                                :{element.line_number}
                                            </Tag>
                                            <div
                                                className={
                                                    Classes.TEXT_OVERFLOW_ELLIPSIS
                                                }
                                            >
                                                {element.source_code}
                                            </div>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                )}
            </HTMLTable>
        </div>
    );
}

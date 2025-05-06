import { FAIcon } from "@/components/FAIcon";
import Timestamp from "@/components/Timestamp";
import { AppToaster } from "@/components/toaster";
import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    ButtonVariant,
    Classes,
    Colors,
    Divider,
    HTMLTable,
    Intent,
    Size,
    Tag,
} from "@blueprintjs/core";
import {
    faCircleCheck,
    faCopy,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useShallow } from "zustand/react/shallow";
import MessageIcon from "../messages/MessageIcon";
export default function MessageViewer({ sessionId, message }) {
    const { session } = useSessionStore(
        useShallow((state) => ({
            session: _.get(state, ["sessions", sessionId], {}),
        }))
    );
    const stream = _.get(session, ["streams", message.stream], null);
    const streamData = _.get(stream, "data", []);
    const tags = _.entries(_.get(message, "metadata.tags", {}))
        .filter((tag) => tag[1])
        .map((tag) => tag[0]);
    return (
        <div
            className="full-parent-dimension"
            style={{ padding: 20, overflowY: "auto" }}
        >
            <div
                style={{
                    display: "flex",
                    gap: 20,
                    alignItems: "center",
                    marginBottom: 10,
                }}
            >
                <div style={{ maxWidth: 71, width: "fit-content" }}>
                    <Tag size={Size.LARGE} minimal intent={Intent.PRIMARY}>
                        {message.contentType}
                    </Tag>
                </div>
                <div
                    style={{
                        display: "flex",
                        maxWidth: "calc(100% - 91px)",
                        gap: 10,
                    }}
                >
                    <div
                        className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                        style={{
                            maxWidth: "calc(100% - 30px)",
                            lineHeight: "30px",
                        }}
                    >
                        {message.stream}
                    </div>
                    <Button
                        onClick={() => {
                            copy(message.stream);
                            AppToaster.show({
                                message: "Stream key name copied",
                            });
                        }}
                        variant={ButtonVariant.MINIMAL}
                        icon={<FAIcon icon={faCopy} />}
                    />
                </div>
            </div>
            <div
                style={{
                    display: "flex",
                    gap: 10,
                    alignItems: "center",
                    marginBottom: 15,
                }}
            >
                <div className={Classes.TEXT_MUTED}>Time</div>
                <Timestamp placement="bottom" date={message.timestamp} />
                <Divider style={{ height: "10px" }} />
                <div className={Classes.TEXT_MUTED}>Created By</div>
                <MessageIcon metadata={message.metadata} />
                <Divider style={{ height: "10px" }} />
                <div className={Classes.TEXT_MUTED}>Tags</div>
                <div style={{ display: "flex", gap: 5 }}>
                    {tags.map((tag) => (
                        <Tag minimal>{tag}</Tag>
                    ))}
                </div>
            </div>
            <HTMLTable
                striped
                bordered
                className="custom-card full-parent-width"
            >
                <thead>
                    <tr>
                        <th>Entry ID</th>
                        <th>Label</th>
                        <th>Content</th>
                        <th>Type</th>
                    </tr>
                </thead>
                <tbody>
                    {streamData.map((data) => (
                        <tr>
                            <td>
                                <div style={{ maxWidth: 200 }}>
                                    <div>
                                        {new Date(
                                            data.timestamp
                                        ).toLocaleTimeString()}
                                        &nbsp;at&nbsp;
                                        {new Date(
                                            data.timestamp
                                        ).toLocaleDateString()}
                                    </div>
                                    <div className={Classes.TEXT_MUTED}>
                                        {data.id}
                                    </div>
                                </div>
                            </td>
                            <td>{data.label}</td>
                            <td>{data.content}</td>
                            <td>{data.dataType}</td>
                        </tr>
                    ))}
                </tbody>
                {stream.complete && (
                    <tfoot>
                        <tr>
                            <td colSpan={4}>
                                EOS
                                <FAIcon
                                    style={{
                                        marginLeft: 10,
                                        color: Colors.GREEN3,
                                    }}
                                    icon={faCircleCheck}
                                />
                            </td>
                        </tr>
                    </tfoot>
                )}
            </HTMLTable>
        </div>
    );
}

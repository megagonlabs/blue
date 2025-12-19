import { useToaster } from "@/components/contexts/ToasterContext";
import { FAIcon } from "@/components/FAIcon";
import Timestamp from "@/components/Timestamp";
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
    faCheckCircle,
    faCopy,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useShallow } from "zustand/react/shallow";
import MessageIcon from "../messages/MessageIcon";
export default function MessageViewer({
    sessionId,
    message,
    showFullContent = false,
}) {
    const { session } = useSessionStore(
        useShallow((state) => ({
            session: _.get(state, ["sessions", sessionId], {}),
        }))
    );
    const { appToaster } = useToaster();
    if (message === null) {
        return null;
    }
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
                <div style={{ maxWidth: 110, width: "fit-content" }}>
                    <Tag
                        size={Size.LARGE}
                        minimal
                        intent={
                            message.contentType === "ERROR"
                                ? Intent.DANGER
                                : Intent.PRIMARY
                        }
                    >
                        {message.contentType}
                    </Tag>
                </div>
                <div
                    style={{
                        display: "flex",
                        maxWidth: "calc(100% - 130px)",
                        gap: 10,
                    }}
                >
                    <div
                        className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                        style={{ lineHeight: "30px" }}
                    >
                        {message.stream}
                    </div>
                    <Button
                        onClick={() => {
                            copy(message.stream);
                            appToaster.show({
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
                    flexWrap: "wrap",
                }}
            >
                <div style={{ display: "inline-flex", gap: 10 }}>
                    <div className={Classes.TEXT_MUTED}>Time</div>
                    <Timestamp placement="bottom" epoch={message.timestamp} />
                </div>
                <Divider style={{ height: "10px" }} />
                <div
                    style={{
                        display: "inline-flex",
                        gap: 10,
                        alignItems: "center",
                    }}
                >
                    <div className={Classes.TEXT_MUTED}>Created By</div>
                    <MessageIcon metadata={message.metadata} />
                </div>
                <Divider style={{ height: "10px" }} />
                <div style={{ display: "inline-flex", gap: 10 }}>
                    <div className={Classes.TEXT_MUTED}>Tags</div>
                    <div style={{ display: "flex", gap: 5 }}>
                        {tags.map((tag) => (
                            <Tag key={tag} minimal>
                                {tag}
                            </Tag>
                        ))}
                    </div>
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
                    {streamData.map((data, index) => (
                        <tr key={index}>
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
                            <td>
                                <div
                                    className={
                                        showFullContent
                                            ? null
                                            : "multiline-ellipsis-5"
                                    }
                                >
                                    {JSON.stringify(data.content)}
                                </div>
                            </td>
                            <td>{data.dataType}</td>
                        </tr>
                    ))}
                </tbody>
                {stream.complete && (
                    <tfoot>
                        <tr>
                            <td colSpan={4}>
                                <div
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                    }}
                                >
                                    EOS
                                    <FAIcon
                                        style={{
                                            marginLeft: 10,
                                            color: Colors.GREEN3,
                                        }}
                                        icon={faCheckCircle}
                                    />
                                </div>
                            </td>
                        </tr>
                    </tfoot>
                )}
            </HTMLTable>
        </div>
    );
}

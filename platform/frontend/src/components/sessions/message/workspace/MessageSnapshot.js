import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import MessageContent from "@/components/sessions/message/MessageContent";
import {
    Button,
    Classes,
    Intent,
    Popover,
    Section,
    SectionCard,
    Tooltip,
} from "@blueprintjs/core";
import { faMessage, faTrash } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext } from "react";
export default function MessageSnapshot({ content, hasError, index }) {
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const streams = appState.session.sessions[sessionIdFocus].streams;
    const stream = _.get(content, "message.stream", null);
    const streamData = _.get(streams, [stream, "data"], []);
    const contentType = _.get(content, "message.contentType", null);
    return (
        <Section
            collapsible
            title="Message"
            icon={faIcon({ icon: faMessage })}
            compact
            rightElement={
                <div onClick={(event) => event.stopPropagation()}>
                    <Popover
                        content={
                            <div style={{ padding: 15 }}>
                                <Button
                                    intent={Intent.DANGER}
                                    className={Classes.POPOVER_DISMISS}
                                    text="Confirm"
                                    onClick={() => {
                                        console.log(index);
                                    }}
                                />
                            </div>
                        }
                        placement="bottom"
                    >
                        <Tooltip placement="bottom" minimal content="Remove">
                            <Button
                                minimal
                                intent={Intent.DANGER}
                                icon={faIcon({ icon: faTrash })}
                            />
                        </Tooltip>
                    </Popover>
                </div>
            }
        >
            <SectionCard
                style={{
                    overflowX: "auto",
                    position: "relative",
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-all",
                }}
            >
                <MessageContent
                    contentType={contentType}
                    streamData={streamData}
                    hasError={hasError}
                />
            </SectionCard>
        </Section>
    );
}

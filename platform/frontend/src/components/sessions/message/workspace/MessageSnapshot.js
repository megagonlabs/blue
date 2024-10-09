import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import MessageContent from "@/components/sessions/message/MessageContent";
import { Section, SectionCard } from "@blueprintjs/core";
import { faMessage } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext } from "react";
export default function MessageSnapshot({ content, hasError }) {
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const streams = appState.session.sessions[sessionIdFocus].streams;
    const stream = _.get(content, "message.stream", null);
    const streamData = _.get(streams, [stream, "data"], []);
    const contentType = _.get(content, "message.contentType", null);
    return (
        <Section title="Message" icon={faIcon({ icon: faMessage })} compact>
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

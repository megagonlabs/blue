import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import MessageContent from "@/components/sessions/message/MessageContent";
import { Section, SectionCard } from "@blueprintjs/core";
import { faMessage } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext } from "react";
export default function Snapshot({ content, index, hasError }) {
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const streams = appState.session.sessions[sessionIdFocus].streams;
    const stream = _.get(content, "message.stream", null);
    const streamData = _.get(streams, [stream, "data"], []);
    const contentType = _.get(content, "message.contentType", null);
    return (
        <Section
            style={{ marginTop: index > 0 ? 20 : 0 }}
            title="Session"
            icon={faIcon({ icon: faMessage })}
            compact
        >
            <SectionCard style={{ overflowX: "auto" }}>
                <MessageContent
                    contentType={contentType}
                    streamData={streamData}
                    hasError={hasError}
                />
            </SectionCard>
        </Section>
    );
}

import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { Colors, Tag } from "@blueprintjs/core";
import {
    faBracketsCurly,
    faEllipsisH,
    faPenLine,
    faQuestion,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
export default function SessionRow({ index, style }) {
    const { appState } = useContext(AppContext);
    const { groupedSessionIds, sessions } = appState.session;
    const sessionId = groupedSessionIds[index];
    const messages = _.get(sessions, [sessionId, "messages"], []);
    const streams = _.get(sessions, [sessionId, "streams"], {});
    const [lastMessage, setLastMessage] = useState("-");
    useEffect(() => {
        const lastMessage = _.last(messages);
        if (_.isEmpty(lastMessage)) {
            setLastMessage("-");
        } else {
            const complete = _.get(
                streams,
                [lastMessage.stream, "complete"],
                false
            );
            if (!complete) {
                setLastMessage(
                    <Tag
                        minimal
                        icon={faIcon({
                            icon: faEllipsisH,
                            size: 16.5,
                            className: "fa-fade",
                            style: { color: Colors.BLACK },
                        })}
                    />
                );
            } else {
                const contentType = _.get(lastMessage, "contentType", null);
                if (_.includes(["STR", "INT", "FLOAT"], contentType)) {
                    const data = _.get(
                        streams,
                        [lastMessage.stream, "data"],
                        []
                    );
                    setLastMessage(_.join(_.map(data, "content"), " "));
                } else if (_.isEqual(contentType, "JSON")) {
                    setLastMessage(
                        <Tag minimal icon={faIcon({ icon: faBracketsCurly })}>
                            JSON
                        </Tag>
                    );
                } else if (_.isEqual(contentType, "JSON_FORM")) {
                    setLastMessage(
                        <Tag minimal icon={faIcon({ icon: faPenLine })}>
                            FORM
                        </Tag>
                    );
                } else {
                    setLastMessage(
                        <Tag minimal icon={faIcon({ icon: faQuestion })}>
                            UNKNOWN
                        </Tag>
                    );
                }
            }
        }
    }, [messages, streams]);
    return lastMessage;
}

import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import MessageSnapshot from "@/components/sessions/message/workspace/MessageSnapshot";
import { Callout, Intent, NonIdealState } from "@blueprintjs/core";
import { faLampDesk } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext, useRef } from "react";
export default function Workspace() {
    const { appState } = useContext(AppContext);
    const { sessionWorkspace, sessionIdFocus } = appState.session;
    const hasError = useRef(false);
    const contents = _.get(sessionWorkspace, sessionIdFocus, []);
    if (_.isEmpty(contents)) {
        return (
            <NonIdealState
                icon={faIcon({ icon: faLampDesk, size: 50 })}
                title="Workspace"
            />
        );
    }
    return (
        <div
            className="full-parent-height"
            style={{ padding: 20, overflowY: "auto" }}
        >
            {contents.map((content, index) => {
                const { type } = content;
                if (!hasError.current) {
                    if (_.isEqual(type, "session")) {
                        return (
                            <MessageSnapshot
                                hasError={hasError}
                                key={index}
                                index={index}
                                content={content}
                            />
                        );
                    }
                }
                return (
                    <div key={index}>
                        <Callout
                            style={{ marginTop: index > 0 ? 20 : 0 }}
                            intent={Intent.DANGER}
                            icon={null}
                            title="Unable to display the content"
                        >
                            We&apos;re unable to read the source data of this
                            content
                        </Callout>
                    </div>
                );
            })}
        </div>
    );
}

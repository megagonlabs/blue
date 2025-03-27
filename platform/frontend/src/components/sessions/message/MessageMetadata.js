import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import Timestamp from "@/components/Timestamp";
import { Classes, Tag } from "@blueprintjs/core";
import classNames from "classnames";
import _ from "lodash";
import { memo, useContext } from "react";
function MessageMetadata({ message }) {
    const { appState } = useContext(AppContext);
    const { propertyLookups } = appState.agent;
    const { settings } = useContext(AuthContext);
    const debugMode = _.get(settings, "debug_mode", false);
    const uid = _.get(message, "metadata.id", null);
    const created_by = _.get(message, "metadata.created_by", null);
    const displayName = _.get(
        propertyLookups,
        [created_by, "display_name"],
        null
    );
    const hasUserProfile = _.has(appState, ["app", "users", uid]);
    const user = _.get(appState, ["app", "users", uid], {});
    const timestamp = message.timestamp;
    return (
        <>
            <div
                className={classNames(Classes.TEXT_OVERFLOW_ELLIPSIS)}
                style={{
                    marginBottom: 5,
                    lineHeight: "20px",
                    display: "flex",
                    gap: 5,
                }}
            >
                <span style={{ fontWeight: 600 }}>
                    {_.isEqual(created_by, "USER")
                        ? hasUserProfile
                            ? user.name
                            : uid
                        : !_.isEmpty(displayName)
                        ? displayName
                        : created_by}
                </span>
                {_.get(
                    appState,
                    ["agent", "systemAgents", created_by],
                    false
                ) ? (
                    <Tag minimal style={{ minWidth: 60.16 }}>
                        SYSTEM
                    </Tag>
                ) : null}
                <Timestamp timestamp={timestamp} />
            </div>
            {debugMode ? (
                <div
                    style={{ marginBottom: 10, lineHeight: "15px" }}
                    className={classNames(
                        Classes.TEXT_DISABLED,
                        Classes.TEXT_SMALL,
                        Classes.TEXT_OVERFLOW_ELLIPSIS
                    )}
                >
                    {message.stream}
                </div>
            ) : null}
        </>
    );
}
export default memo(MessageMetadata);

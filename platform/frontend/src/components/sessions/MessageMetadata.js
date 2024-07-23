import { PROFILE_PICTURE_40 } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { getAgentFromStream } from "@/components/helper";
import { Card, Classes } from "@blueprintjs/core";
import _ from "lodash";
import Image from "next/image";
import { memo, useContext, useEffect } from "react";
import ReactTimeAgo from "react-time-ago";
function MessageMetadata({ timestamp, stream }) {
    const { appState, appActions } = useContext(AppContext);
    const agent = getAgentFromStream(stream);
    const agentType = _.get(agent, "type", null);
    const agentId = _.get(agent, "id", null);
    const hasUserProfile = _.has(appState, ["app", "users", agentId]);
    const user = _.get(appState, ["app", "users", agentId], {});
    useEffect(() => {
        if (!hasUserProfile && _.isEqual(agentType, "USER")) {
            appActions.app.getUserProfile(agentId);
        }
    }, []);
    return (
        <>
            <ReactTimeAgo date={new Date(timestamp)} locale="en-US" />
            <div className={Classes.TEXT_DISABLED}>
                {new Date(timestamp).toLocaleDateString()}
                &nbsp;at&nbsp;
                {new Date(timestamp).toLocaleTimeString()}
            </div>
            {_.isEqual(agentType, "USER") ? (
                <>
                    <br />
                    <div
                        className={!hasUserProfile ? Classes.SKELETON : null}
                        style={{ display: "flex", alignItems: "center" }}
                    >
                        <Card className="margin-0" style={PROFILE_PICTURE_40}>
                            <Image
                                alt=""
                                src={_.get(user, "picture", "")}
                                width={40}
                                height={40}
                            />
                        </Card>
                        <div
                            className={Classes.TEXT_MUTED}
                            style={{ marginLeft: 12 }}
                        >
                            {_.get(user, "name", "-")}
                            <br />
                            {_.get(user, "email", "-")}
                        </div>
                    </div>
                </>
            ) : null}
        </>
    );
}
export default memo(MessageMetadata);

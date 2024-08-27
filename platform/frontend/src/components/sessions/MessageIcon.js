import { ENTITY_ICON_40, PROFILE_PICTURE_40 } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { Card, Classes } from "@blueprintjs/core";
import _ from "lodash";
import Image from "next/image";
import { memo, useContext, useEffect } from "react";
import EntityIcon from "../entity/EntityIcon";
function MessageIcon({ message }) {
    const { appState, appActions } = useContext(AppContext);
    const uid = _.get(message, "metadata.id", null);
    const created_by = _.get(message, "metadata.created_by", null);
    const hasUserProfile = _.has(appState, ["app", "users", uid]);
    const user = _.get(appState, ["app", "users", uid], {});
    useEffect(() => {
        if (!hasUserProfile && _.isEqual(created_by, "USER")) {
            appActions.app.getUserProfile(uid);
        } else if (!_.has(appState, ["agent", "icon", created_by])) {
            appActions.agent.fetchIcon(created_by);
        }
    }, []);
    return _.isEqual(created_by, "USER") ? (
        <Card
            style={PROFILE_PICTURE_40}
            className={!hasUserProfile ? Classes.SKELETON : null}
        >
            <Image
                alt=""
                src={_.get(user, "picture", "")}
                width={40}
                height={40}
            />
        </Card>
    ) : (
        <Card style={ENTITY_ICON_40}>
            <EntityIcon
                entity={{
                    type: "agent",
                    icon: _.get(appState, ["agent", "icon", created_by]),
                }}
            />
        </Card>
    );
}
export default memo(MessageIcon);

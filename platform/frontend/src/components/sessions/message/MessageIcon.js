import { ENTITY_ICON_40, PROFILE_PICTURE_40 } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { Card, Classes, Icon } from "@blueprintjs/core";
import { faQuestion } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import Image from "next/image";
import { memo, useContext } from "react";
import EntityIcon from "../../entity/EntityIcon";
function MessageIcon({ message }) {
    const { appState } = useContext(AppContext);
    const uid = _.get(message, "metadata.id", null);
    const created_by = _.get(message, "metadata.created_by", null);
    const hasUserProfile = _.has(appState, ["app", "users", uid]);
    const user = _.get(appState, ["app", "users", uid], {});
    return _.isEqual(created_by, "USER") ? (
        <Card
            style={PROFILE_PICTURE_40}
            className={!hasUserProfile ? Classes.SKELETON : null}
        >
            {_.isEmpty(user) ? (
                <Icon icon={faIcon({ icon: faQuestion, size: 20 })} />
            ) : (
                <Image alt="" src={user.picture} width={40} height={40} />
            )}
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

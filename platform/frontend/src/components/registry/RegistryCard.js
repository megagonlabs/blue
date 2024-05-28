import { Card, Colors, H5, Intent, Tag, Tooltip } from "@blueprintjs/core";
import { faCircleDot } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import Link from "next/link";
import { faIcon } from "../icon";
export default function RegistryCard({
    title,
    description,
    href,
    extra,
    container,
}) {
    const containerStatus = _.get(container, "status", "not exist");
    const CONTAINER_STATUS_INDICATOR = {
        created: { style: { color: Colors.GOLD4 } },
        running: { style: { color: Colors.GREEN4 } },
        paused: { style: { color: Colors.RED4 } },
        restarting: { style: { color: Colors.GOLD4 } },
        exited: { style: { color: Colors.RED4 } },
        removing: { style: { color: Colors.RED4 } },
        dead: { style: { color: Colors.RED4 } },
    };
    return (
        <Link className="no-link-decoration" href={href}>
            <Card
                style={{
                    height: "100%",
                    backgroundColor: Colors.LIGHT_GRAY5,
                    position: "relative",
                }}
            >
                <H5>{title}</H5>
                <div className="multiline-ellipsis" style={{ height: 36 }}>
                    {description}
                </div>
                {!_.isEmpty(extra) ? (
                    <Tag
                        style={{
                            marginTop: 10,
                            maxWidth: `calc(100% - ${
                                _.isEqual(containerStatus, "not exist") ? 0 : 36
                            }px)`,
                        }}
                        large
                        minimal
                        intent={Intent.PRIMARY}
                    >
                        {extra}
                    </Tag>
                ) : null}
                {!_.isEqual(containerStatus, "not exist") ? (
                    <div
                        style={{ position: "absolute", bottom: 27, right: 20 }}
                    >
                        <Tooltip
                            minimal
                            placement="left"
                            content={containerStatus}
                        >
                            {faIcon({
                                icon: faCircleDot,
                                ...CONTAINER_STATUS_INDICATOR[containerStatus],
                            })}
                        </Tooltip>
                    </div>
                ) : null}
            </Card>
        </Link>
    );
}

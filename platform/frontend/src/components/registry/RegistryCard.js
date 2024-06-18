import { CONTAINER_STATUS_INDICATOR } from "@/components/constant";
import { faIcon } from "@/components/icon";
import { Card, Colors, H5, Intent, Tag, Tooltip } from "@blueprintjs/core";
import { faCircleDot } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import Link from "next/link";
export default function RegistryCard({
    title,
    description,
    href,
    extra,
    container,
}) {
    const containerStatus = _.get(container, "status", "not exist");
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
                        minimal
                        intent={Intent.PRIMARY}
                    >
                        {extra}
                    </Tag>
                ) : null}
                {!_.isEqual(containerStatus, "not exist") ? (
                    <div
                        style={{ position: "absolute", bottom: 21, right: 20 }}
                    >
                        <Tooltip
                            minimal
                            placement="left"
                            content={containerStatus}
                        >
                            {faIcon({
                                icon: faCircleDot,
                                style: _.get(
                                    CONTAINER_STATUS_INDICATOR,
                                    [containerStatus, "style"],
                                    null
                                ),
                            })}
                        </Tooltip>
                    </div>
                ) : null}
            </Card>
        </Link>
    );
}

import { CONTAINER_STATUS_INDICATOR } from "@/components/constant";
import { faIcon } from "@/components/icon";
import {
    Card,
    Classes,
    Colors,
    H5,
    Intent,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { faCircleDot } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import Link from "next/link";
import EntityIcon from "../entity/EntityIcon";
export default function RegistryCard({
    type,
    title,
    icon,
    description,
    href = "",
    extra,
    container,
}) {
    const containerStatus = _.get(container, "status", "not exist");
    return (
        <Link
            style={
                _.isEmpty(href)
                    ? { cursor: "initial", pointerEvents: "none" }
                    : null
            }
            className="no-link-decoration"
            href={href}
        >
            <Card
                style={{
                    height: "100%",
                    backgroundColor: Colors.LIGHT_GRAY5,
                    position: "relative",
                }}
            >
                <Card
                    style={{
                        position: "absolute",
                        left: 20,
                        top: 20,
                        overflow: "hidden",
                        padding: 0,
                        height: 40,
                        width: 40,
                        display: "flex",
                        justifyContent: "center",
                        alignItems: "center",
                    }}
                >
                    <EntityIcon entity={{ icon, type }} />
                </Card>
                <H5
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                    style={{
                        lineHeight: "40px",
                        marginLeft: 50,
                        marginBottom: 0,
                    }}
                >
                    {title}
                </H5>
                <div
                    className="multiline-ellipsis-2"
                    style={{ height: 36, marginTop: 10 }}
                >
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

import { Card, Classes, Colors, Intent, Tag } from "@blueprintjs/core";
import { faDocker } from "@fortawesome/free-brands-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useEffect, useState } from "react";
import { DOCKER_CONTAINER_STATUS_LOOKUP } from "../constants";
import { FAIcon } from "../FAIcon";
import RegistryEntityIcon from "./RegistryEntityIcon";
export default function RegistryCard({ entity }) {
    const type = _.get(entity, "type", null);
    const displayName = _.get(entity, "properties.display_name", entity.name);
    const categories = _.get(entity, "property.categories", ["BASE", "HIDDEN"]);
    const containerStatus = _.get(entity, "container.status", "not exist");
    const [extra, setExtra] = useState(null);
    useEffect(() => {
        if (_.includes(["agent", "operator"], type)) {
            setExtra(_.toString(_.get(entity, "properties.image")));
        } else if (_.isEqual("data", type)) {
            let protocol = _.get(entity, "properties.connection.protocol");
            let host = _.get(entity, "properties.connection.host");
            let port = _.get(entity, "properties.connection.port");
            setExtra(`${protocol}://${host}:${port}`);
        } else {
            setExtra(null);
        }
    }, [entity.properties]);
    return (
        <Card
            className="full-parent-dimension"
            style={{ position: "relative" }}
        >
            <Card
                className="padding-0 overflow-hidden"
                style={{
                    position: "absolute",
                    left: 20,
                    top: 20,
                    height: 40,
                    width: 40,
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    backgroundColor: Colors.WHITE,
                }}
            >
                <RegistryEntityIcon content={_.get(entity, "icon", null)} />
            </Card>
            <div
                style={{
                    marginLeft: 60,
                    display: "flex",
                    flexDirection: "column",
                    height: 40,
                    justifyContent: "space-between",
                }}
            >
                <div
                    style={{ fontWeight: 600 }}
                    className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                >
                    {displayName}
                </div>
                <div
                    className={Classes.TEXT_DISABLED}
                    style={_.get(
                        DOCKER_CONTAINER_STATUS_LOOKUP,
                        [containerStatus, "style"],
                        null
                    )}
                >
                    <FAIcon icon={faDocker} style={{ marginRight: 5 }} />
                    container:&nbsp;{containerStatus}
                </div>
            </div>
            <div
                className={classNames(
                    "multiline-ellipsis-2",
                    Classes.TEXT_MUTED
                )}
                style={{ height: 36, marginTop: 10 }}
            >
                {entity.description}
            </div>
            {!_.isEmpty(categories) && (
                <div
                    className="full-parent-width scrollbar-none"
                    style={{
                        display: "inline-flex",
                        gap: 10,
                        marginTop: 10,
                        overflowX: "auto",
                    }}
                >
                    {categories.map((category, index) => (
                        <Tag
                            key={index}
                            style={{ display: "inline-table" }}
                            minimal
                        >
                            {category}
                        </Tag>
                    ))}
                </div>
            )}
            {!_.isEmpty(extra) && (
                <Tag minimal intent={Intent.PRIMARY} style={{ marginTop: 10 }}>
                    {extra}
                </Tag>
            )}
        </Card>
    );
}

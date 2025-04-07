import { Card, Colors, H5, Tag } from "@blueprintjs/core";
import _ from "lodash";
import RegistryEntityIcon from "./RegistryEntityIcon";
export default function RegistryCard({ entity }) {
    const displayName = _.get(entity, "properties.display_name", entity.name);
    const categories = _.get(entity, "property.categories", []);
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
            <H5 style={{ marginLeft: 50, lineHeight: "40px" }}>
                {displayName}
            </H5>
            <div
                className="multiline-ellipsis-2"
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
        </Card>
    );
}

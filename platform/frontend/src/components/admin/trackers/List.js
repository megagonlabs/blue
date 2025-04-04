import { AuthContext } from "@/components/contexts/auth-context";
import { faIcon } from "@/components/icon";
import {
    Card,
    Classes,
    Colors,
    Divider,
    H6,
    Popover,
    Tag,
} from "@blueprintjs/core";
import { faList } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext } from "react";
export default function List({ label, object }) {
    const { settings } = useContext(AuthContext);
    const darkMode = _.get(settings, "dark_mode", false);
    const render = (object) => {
        let result = [];
        let { type, label, visibility, data } = object;
        if (visibility) {
            if (_.isEqual(type, "group")) {
                let keys = Object.keys(data);
                let group = [];
                result.push(
                    <H6
                        style={{ marginBottom: 5 }}
                        className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                    >
                        {label}
                    </H6>
                );
                for (let i = 0; i < _.size(keys); i++) {
                    group = group.concat(render(data[keys[i]]));
                }
                result.push(
                    <div
                        className="full-parent-width"
                        style={{ display: "flex", gap: 5, flexWrap: "wrap" }}
                    >
                        {group.map((e, index) => (
                            <div key={index}>{e}</div>
                        ))}
                    </div>
                );
            } else if (
                ["alive", "tag", "number", "text", "status", "time"].includes(
                    type
                )
            ) {
                result.push(
                    <Tag minimal>
                        {label}: {_.toString(_.get(object, "value", ""))}
                    </Tag>
                );
            } else if (_.isEqual(type, "list")) {
                let keys = Object.keys(data);
                for (let i = 0; i < _.size(keys); i++) {
                    result.push(render(data[keys[i]]));
                }
            }
        }
        return result;
    };
    return (
        <Popover
            content={
                <div
                    style={{
                        padding: 15,
                        overflow: "auto",
                        maxHeight: 400,
                        maxWidth: 400,
                    }}
                >
                    {render(object).map((e, index) => (
                        <div key={index}>
                            {index > 0 && (
                                <Divider
                                    style={{ marginTop: 10, marginBottom: 10 }}
                                />
                            )}
                            {e}
                        </div>
                    ))}
                </div>
            }
        >
            <Card
                style={{
                    cursor: "pointer",
                    padding: darkMode ? 1 : 0,
                    overflow: "hidden",
                }}
            >
                <div
                    style={{ padding: "10px 10px 5px" }}
                    className={Classes.TEXT_MUTED}
                >
                    {label}
                </div>
                <div
                    style={{
                        height: "50%",
                        padding: "5px 10px 10px",
                        backgroundColor: darkMode
                            ? Colors.DARK_GRAY3
                            : Colors.LIGHT_GRAY5,
                    }}
                >
                    {faIcon({ icon: faList })}
                </div>
            </Card>
        </Popover>
    );
}

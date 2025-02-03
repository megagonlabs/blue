import SessionConfigs from "@/components/admin/configs/SessionConfigs";
import { faIcon } from "@/components/icon";
import { Button, ButtonGroup, Card, H4 } from "@blueprintjs/core";
import { faInboxFull } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useEffect, useState } from "react";
const INDEXES = [
    {
        key: "session",
        text: "Sessions",
        icon: faInboxFull,
    },
];
export default function Configs() {
    const [loading, setLoading] = useState(false);
    const [configs, setConfigs] = useState({});
    useEffect(() => {
        setLoading(true);
        axios.get("/platform/settings").then((response) => {
            setConfigs(_.get(response, "data.settings", {}));
            setLoading(false);
        });
    }, []);
    return (
        <>
            <Card
                style={{
                    padding: 5,
                    borderRadius: 0,
                    position: "relative",
                    zIndex: 1,
                    cursor: "default",
                }}
            >
                <ButtonGroup large minimal>
                    <Button
                        disabled
                        style={{ cursor: "default" }}
                        text={<H4 className="margin-0">Configs</H4>}
                    />
                </ButtonGroup>
            </Card>
            <Card
                style={{ padding: 5, position: "absolute", top: 70, left: 20 }}
            >
                <ButtonGroup vertical large minimal>
                    {INDEXES.map(({ key, text, icon }) => (
                        <Button
                            icon={faIcon({
                                icon: icon,
                                style: { marginRight: 10 },
                            })}
                            key={key}
                            text={text}
                            onClick={() => {
                                const element = _.first(
                                    document.getElementsByClassName(
                                        `admin-configs-${key}`
                                    )
                                );
                                if (element) {
                                    element.scrollIntoView({
                                        behavior: "smooth",
                                    });
                                }
                            }}
                        />
                    ))}
                </ButtonGroup>
            </Card>
            <div
                className="full-parent-width"
                style={{
                    overflowY: "auto",
                    height: "calc(100% - 50px)",
                    padding: "20px 20px 20px 170.55px",
                }}
            >
                <div
                    className="admin-configs-session"
                    style={{ scrollMargin: 20 }}
                >
                    <SessionConfigs
                        loading={loading}
                        configs={configs}
                        setLoading={setLoading}
                    />
                </div>
            </div>
        </>
    );
}

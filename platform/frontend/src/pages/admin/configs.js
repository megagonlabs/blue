import EmailAllowlist from "@/components/admin/configs/EmailAllowlist";
import SessionConfigs from "@/components/admin/configs/SessionConfigs";
import { faIcon } from "@/components/icon";
import { Alignment, Button, ButtonGroup, Card, H4 } from "@blueprintjs/core";
import {
    faEnvelopes,
    faInboxFull,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useEffect, useState } from "react";
const INDEXES = [
    {
        key: "sessions",
        text: "Sessions",
        icon: faInboxFull,
    },
    {
        key: "email-allowlist",
        text: "Email Allowlist",
        icon: faEnvelopes,
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
                <ButtonGroup size="large" variant="minimal">
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
                <ButtonGroup
                    alignText={Alignment.START}
                    vertical
                    size="large"
                    variant="minimal"
                >
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
                    padding: "20px 20px 20px 208.61px",
                }}
            >
                <div
                    className="admin-configs-sessions"
                    style={{ scrollMargin: 20 }}
                >
                    <SessionConfigs loading={loading} configs={configs} />
                </div>
                <div
                    className="admin-configs-email-allowlist"
                    style={{ scrollMargin: 20, marginTop: 20 }}
                >
                    <EmailAllowlist loading={loading} configs={configs} />
                </div>
            </div>
        </>
    );
}

import { AppToaster } from "@/components/toaster";
import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    Classes,
    Code,
    Colors,
    H3,
    Intent,
    Popover,
} from "@blueprintjs/core";
import axios from "axios";
import { useState } from "react";
export default function SessionSettings({ sessionId }) {
    const [loading, setLoading] = useState(false);
    const removeSession = useSessionStore((state) => state.removeSession);
    const deleteSession = () => {
        setLoading(true);
        axios
            .delete(`/sessions/session/${sessionId}`)
            .then(() => {
                removeSession(sessionId);
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: "Session deleted",
                });
            })
            .finally(() => {
                setLoading(false);
            });
    };
    return (
        <div className="full-parent-dimension" style={{ padding: 20 }}>
            <H3>Danger Zone</H3>
            <div
                className="custom-card"
                style={{ border: `1px solid ${Colors.RED3}`, padding: 20 }}
            >
                <div>
                    <div style={{ fontWeight: 600 }}>Delete this session</div>
                    <div>
                        Once you delete this session, its <Code>STREAM</Code>
                        ,&nbsp;<Code>DATA</Code> and <Code>METADATA</Code> will
                        be removed.
                    </div>
                    <div style={{ marginTop: 20 }}></div>
                    <Popover
                        placement="right"
                        content={
                            <div style={{ padding: 10 }}>
                                <Button
                                    className={Classes.POPOVER_DISMISS}
                                    intent={Intent.DANGER}
                                    onClick={deleteSession}
                                    text="Confirm"
                                />
                            </div>
                        }
                    >
                        <Button
                            loading={loading}
                            intent={Intent.DANGER}
                            text="Delete this session"
                        />
                    </Popover>
                </div>
            </div>
        </div>
    );
}

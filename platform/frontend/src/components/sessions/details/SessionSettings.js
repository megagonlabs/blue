import { AppContext } from "@/components/contexts/app-context";
import {
    Button,
    Card,
    Classes,
    Code,
    DialogBody,
    Intent,
    Popover,
} from "@blueprintjs/core";
import axios from "axios";
import { useRouter } from "next/router";
import { useContext, useState } from "react";
export default function SessionSettings() {
    const { appState, appActions } = useContext(AppContext);
    const { sessionIdFocus } = appState.session;
    const router = useRouter();
    const [deleting, setDeleting] = useState(false);
    const deleteSession = () => {
        if (!router.isReady) return;
        setDeleting(true);
        axios
            .delete(`/sessions/session/${sessionIdFocus}`)
            .then(() => {
                appActions.session.setState({
                    key: "sessionIdFocus",
                    value: null,
                });
                appActions.session.removeSession(sessionIdFocus);
            })
            .finally(() => setDeleting(false));
        router.push("/sessions");
    };
    return (
        <>
            <DialogBody>
                <Card compact>
                    <div
                        style={{
                            display: "flex",
                            gap: 15,
                            alignItems: "center",
                            justifyContent: "space-between",
                        }}
                    >
                        <div
                            style={{
                                maxWidth: "calc(100% - 181.26px)",
                            }}
                        >
                            <label style={{ fontWeight: 600 }}>
                                Delete this session
                            </label>
                            <div>
                                Once you delete this session, its&nbsp;
                                <Code>STREAM</Code>,&nbsp;<Code>DATA</Code>
                                &nbsp;and&nbsp;
                                <Code>METADATA</Code>&nbsp;will be removed.
                            </div>
                        </div>
                        <div>
                            <Popover
                                usePortal={false}
                                placement="left"
                                content={
                                    <div style={{ padding: 15 }}>
                                        <Button
                                            size="large"
                                            className={Classes.POPOVER_DISMISS}
                                            text="Confirm"
                                            onClick={deleteSession}
                                            intent={Intent.DANGER}
                                        />
                                    </div>
                                }
                            >
                                <Button
                                    size="large"
                                    loading={deleting}
                                    intent={Intent.DANGER}
                                    text="Delete this session"
                                />
                            </Popover>
                        </div>
                    </div>
                </Card>
            </DialogBody>
        </>
    );
}

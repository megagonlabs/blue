import { AppContext } from "@/components/contexts/app-context";
import {
    Button,
    Card,
    Classes,
    DialogBody,
    Intent,
    Popover,
} from "@blueprintjs/core";
import axios from "axios";
import { useContext, useState } from "react";
export default function SessionSettings() {
    const { appState, appActions } = useContext(AppContext);
    const { sessionIdFocus } = appState.session;
    const [deleting, setDeleting] = useState(false);
    const deleteSession = () => {
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
    };
    return (
        <>
            <DialogBody className="dialog-body">
                <div style={{ padding: 15 }}>
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
                                    maxWidth: "calc(100% - 156.57px)",
                                }}
                            >
                                <label style={{ fontWeight: 600 }}>
                                    Delete this session
                                </label>
                                <div>
                                    Once you delete this session, its STREAM,
                                    DATA and METADATA will be removed.
                                </div>
                            </div>
                            <div>
                                <Popover
                                    usePortal={false}
                                    placement="left"
                                    content={
                                        <div style={{ padding: 15 }}>
                                            <Button
                                                className={
                                                    Classes.POPOVER_DISMISS
                                                }
                                                text="Confirm"
                                                onClick={deleteSession}
                                                intent={Intent.DANGER}
                                            />
                                        </div>
                                    }
                                >
                                    <Button
                                        loading={deleting}
                                        intent={Intent.DANGER}
                                        text="Delete this session"
                                    />
                                </Popover>
                            </div>
                        </div>
                    </Card>
                </div>
            </DialogBody>
        </>
    );
}

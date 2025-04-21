import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    Classes,
    Colors,
    DialogBody,
    FormGroup,
    InputGroup,
    Intent,
} from "@blueprintjs/core";
import { faCheck } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useState } from "react";
export default function SessionMetadata({
    setAllowQuickClose,
    loading,
    setLoading,
}) {
    const { appState, appActions } = useContext(AppContext);
    const { settings } = useContext(AuthContext);
    const darkMode = _.get(settings, "dark_mode", false);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const sessionDetails = _.get(
        appState,
        ["session", "sessionDetails", sessionIdFocus],
        {}
    );
    const sessionName = _.get(sessionDetails, "name", "");
    const sessionDescription = _.get(sessionDetails, "description", "");
    const [name, setName] = useState(sessionName);
    const [description, setDescription] = useState(sessionDescription);
    const handleSaveMetadata = () => {
        setLoading(true);
        const payload = {
            name: _.trim(name),
            description: _.trim(description),
        };
        axios
            .put(`/sessions/session/${sessionIdFocus}`, payload)
            .then(() => {
                setAllowQuickClose(true);
                setLoading(false);
                appActions.session.setSessionDetails([
                    { ...sessionDetails, ...payload, id: sessionIdFocus },
                ]);
            })
            .catch(() => {
                setAllowQuickClose(true);
                setLoading(false);
            })
            .finally(() =>
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: "Saved",
                })
            );
    };
    return (
        <>
            <DialogBody>
                <div style={{ marginBottom: 15 }}>
                    <span style={{ marginRight: 10 }}>Session ID</span>
                    <span
                        className={Classes.TEXT_MUTED}
                        style={{ fontWeight: 600, lineHeight: "30px" }}
                    >
                        {sessionIdFocus}
                    </span>
                </div>
                <FormGroup label="Name" labelFor="session-detail-name">
                    <InputGroup
                        id="session-detail-name"
                        className={loading ? Classes.SKELETON : null}
                        size="large"
                        value={name}
                        onChange={(event) => {
                            setName(event.target.value);
                            setAllowQuickClose(false);
                        }}
                    />
                </FormGroup>
                <FormGroup
                    label="Description"
                    className="margin-0"
                    labelFor="session-detail-description"
                >
                    <InputGroup
                        id="session-detail-description"
                        className={loading ? Classes.SKELETON : null}
                        size="large"
                        value={description}
                        onChange={(event) => {
                            setDescription(event.target.value);
                            setAllowQuickClose(false);
                        }}
                    />
                </FormGroup>
            </DialogBody>
            <div
                className="border-top"
                style={{
                    padding: "10px 15px",
                    borderBottomRightRadius: 4,
                    backgroundColor: darkMode
                        ? Colors.DARK_GRAY4
                        : Colors.WHITE,
                }}
            >
                <Button
                    disabled={_.isEmpty(_.trim(name))}
                    loading={loading}
                    text="Save"
                    size="large"
                    onClick={handleSaveMetadata}
                    intent={Intent.SUCCESS}
                    icon={faIcon({ icon: faCheck })}
                />
            </div>
        </>
    );
}

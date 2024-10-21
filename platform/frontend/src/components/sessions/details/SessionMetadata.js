import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    Classes,
    DialogBody,
    DialogFooter,
    FormGroup,
    InputGroup,
    Intent,
    Label,
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
            <DialogBody className="dialog-body">
                <div style={{ padding: 15 }}>
                    <FormGroup label="Session ID" inline>
                        <Label
                            className={Classes.TEXT_MUTED}
                            style={{ fontWeight: 600 }}
                        >
                            {sessionIdFocus}
                        </Label>
                    </FormGroup>
                    <FormGroup label="Name">
                        <InputGroup
                            className={loading ? Classes.SKELETON : null}
                            large
                            value={name}
                            onChange={(event) => {
                                setName(event.target.value);
                                setAllowQuickClose(false);
                            }}
                        />
                    </FormGroup>
                    <FormGroup label="Description" className="margin-0">
                        <InputGroup
                            className={loading ? Classes.SKELETON : null}
                            large
                            value={description}
                            onChange={(event) => {
                                setDescription(event.target.value);
                                setAllowQuickClose(false);
                            }}
                        />
                    </FormGroup>
                </div>
            </DialogBody>
            <DialogFooter>
                <Button
                    disabled={_.isEmpty(_.trim(name))}
                    loading={loading}
                    text="Save"
                    large
                    onClick={handleSaveMetadata}
                    intent={Intent.SUCCESS}
                    icon={faIcon({ icon: faCheck })}
                />
            </DialogFooter>
        </>
    );
}

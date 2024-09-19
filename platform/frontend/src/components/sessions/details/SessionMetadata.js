import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    DialogBody,
    DialogFooter,
    FormGroup,
    InputGroup,
    Intent,
} from "@blueprintjs/core";
import { faCheck } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useState } from "react";
export default function SessionMetadata({ allowQuickClose }) {
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
    const [loading, setLoading] = useState(false);
    const handleSaveMetadata = () => {
        setLoading(true);
        const payload = {
            name: _.trim(name),
            description: _.trim(description),
        };
        axios
            .put(`/sessions/session/${sessionIdFocus}`, payload)
            .then(() => {
                allowQuickClose.current = true;
                setLoading(false);
                appActions.session.setSessionDetails([
                    { ...sessionDetails, ...payload, id: sessionIdFocus },
                ]);
            })
            .catch(() => {
                allowQuickClose.current = true;
                setLoading(false);
            })
            .finally(() => {
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: "Saved",
                });
            });
    };
    return (
        <>
            <DialogBody className="dialog-body">
                <div style={{ padding: 15 }}>
                    <FormGroup label="Name">
                        <InputGroup
                            large
                            value={name}
                            onChange={(event) => {
                                setName(event.target.value);
                                allowQuickClose.current = false;
                            }}
                        />
                    </FormGroup>
                    <FormGroup label="Description" className="margin-0">
                        <InputGroup
                            large
                            value={description}
                            onChange={(event) => {
                                setDescription(event.target.value);
                                allowQuickClose.current = false;
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

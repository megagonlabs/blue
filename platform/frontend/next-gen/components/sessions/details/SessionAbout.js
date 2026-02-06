import { useToaster } from "@/components/contexts/ToasterContext";
import { FAIcon } from "@/components/FAIcon";
import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    ButtonVariant,
    Classes,
    FormGroup,
    InputGroup,
    Intent,
    Size,
} from "@blueprintjs/core";
import {
    faCheck,
    faClipboard,
    faCopy,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useEffect, useState } from "react";
import { useShallow } from "zustand/react/shallow";
export default function SessionAbout({ sessionId }) {
    const { sessions, setSessionDetails } = useSessionStore(
        useShallow((state) => ({
            sessions: state.sessions,
            setSessionDetails: state.setSessionDetails,
        }))
    );
    const details = _.get(sessions, [sessionId, "details"], {});
    const [name, setName] = useState(_.get(details, "name", ""));
    const [description, setDescription] = useState(
        _.get(details, "description", "")
    );
    const [loading, setLoading] = useState(false);
    const { appToaster } = useToaster();
    const handleSave = () => {
        setLoading(true);
        const payload = {
            name: _.trim(name),
            description: _.trim(description),
        };
        axios
            .put(`/sessions/session/${sessionId}`, payload)
            .then(() => {
                setSessionDetails({
                    sessionId,
                    fields: [
                        { path: "name", value: payload.name },
                        { path: "description", value: payload.description },
                    ],
                });
            })
            .finally(() => {
                setLoading(false);
                appToaster.show({
                    intent: Intent.SUCCESS,
                    message: "Saved",
                });
            });
    };
    useEffect(() => {
        if (!_.isEqual(details.name, name)) {
            setName(details.name);
        }
        if (!_.isEqual(details.description, description)) {
            setDescription(details.description);
        }
    }, [details.name, details.description]);
    const copySessionId = () => {
        copy(sessionId);
        if (appToaster) {
            appToaster.show({
                icon: <FAIcon icon={faClipboard} />,
                message: "Copied Session ID",
            });
        }
    };
    return (
        <div className="full-parent-dimension" style={{ padding: 20 }}>
            <FormGroup inline label="Session ID">
                <div style={{ display: "flex", alignItems: "center" }}>
                    <div
                        style={{ lineHeight: "30px", marginRight: 16 }}
                        className={Classes.TEXT_MUTED}
                    >
                        {sessionId}
                    </div>
                    <Button
                        onClick={copySessionId}
                        variant={ButtonVariant.MINIMAL}
                        icon={<FAIcon icon={faCopy} />}
                    />
                </div>
            </FormGroup>
            <FormGroup label="Name">
                <InputGroup
                    readOnly={loading}
                    onValueChange={(value) => setName(value)}
                    fill
                    size={Size.LARGE}
                    value={name}
                />
            </FormGroup>
            <FormGroup label="Description">
                <InputGroup
                    readOnly={loading}
                    onValueChange={(value) => setDescription(value)}
                    fill
                    size={Size.LARGE}
                    value={description}
                />
            </FormGroup>
            <Button
                icon={<FAIcon icon={faCheck} />}
                loading={loading}
                size={Size.LARGE}
                onClick={handleSave}
                text="Save"
                intent={Intent.SUCCESS}
            />
        </div>
    );
}

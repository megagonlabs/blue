import { AppContext } from "@/components/contexts/app-context";
import {
    Button,
    Card,
    Dialog,
    FormGroup,
    H4,
    InputGroup,
    Intent,
} from "@blueprintjs/core";
import { faCheck } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { faIcon } from "../icon";
export default function SessionDetail({ isOpen, setIsSessionDetailOpen }) {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [name, setName] = useState(
        _.get(
            appState,
            ["session", "sessionDetail", sessionIdFocus, "name"],
            ""
        )
    );
    const [description, setDescription] = useState(
        _.get(
            appState,
            ["session", "sessionDetail", sessionIdFocus, "description"],
            ""
        )
    );
    const [loading, setLoading] = useState(false);
    const handleSaveMetadata = () => {
        setLoading(true);
        const payload = {
            name: _.trim(name),
            description: _.trim(description),
        };
        axios
            .put(`/sessions/session/${sessionIdFocus}`, payload)
            .then((response) => {
                setLoading(false);
                appActions.session.setSessionDetail([
                    {
                        ...payload,
                        id: sessionIdFocus,
                    },
                ]);
            })
            .catch((error) => {
                setLoading(false);
            });
    };
    useEffect(() => {
        setName(
            _.get(
                appState,
                ["session", "sessionDetail", sessionIdFocus, "name"],
                ""
            )
        );
        setDescription(
            _.get(
                appState,
                ["session", "sessionDetail", sessionIdFocus, "description"],
                ""
            )
        );
    }, [appState.session.sessionDetail, sessionIdFocus]);
    const [tab, setTab] = useState("about");
    return (
        <Dialog
            style={{ padding: 20 }}
            onClose={() => {
                if (loading) {
                    return;
                }
                setIsSessionDetailOpen(false);
            }}
            isOpen={isOpen}
        >
            <H4>{sessionIdFocus}</H4>
            <Card style={{ padding: 5, marginBottom: 20 }}>
                <Button
                    minimal
                    text="About"
                    onClick={() => {
                        setTab("about");
                    }}
                    active={_.isEqual(tab, "about")}
                />
            </Card>
            <FormGroup label="Name">
                <InputGroup
                    large
                    value={name}
                    onChange={(event) => {
                        setName(event.target.value);
                    }}
                />
            </FormGroup>
            <FormGroup label="Description">
                <InputGroup
                    large
                    value={description}
                    onChange={(event) => {
                        setDescription(event.target.value);
                    }}
                />
            </FormGroup>
            <Button
                loading={loading}
                text="Save"
                large
                onClick={handleSaveMetadata}
                style={{ width: 90.96 }}
                intent={Intent.SUCCESS}
                icon={faIcon({ icon: faCheck })}
            />
        </Dialog>
    );
}

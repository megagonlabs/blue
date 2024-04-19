import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import {
    Button,
    Card,
    Dialog,
    DialogBody,
    DialogFooter,
    FormGroup,
    InputGroup,
    Intent,
} from "@blueprintjs/core";
import { faCheck } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
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
    }, [appState.session.sessionDetail, sessionIdFocus, isOpen]);
    const [tab, setTab] = useState("about");
    return (
        <Dialog
            title={sessionIdFocus}
            canOutsideClickClose={false}
            onClose={() => {
                if (loading) return;
                setIsSessionDetailOpen(false);
            }}
            isOpen={isOpen}
            style={{ padding: 0 }}
        >
            <DialogBody className="padding-0">
                <Card style={{ padding: "5px 15px", borderRadius: 0 }}>
                    <Button
                        minimal
                        large
                        text="About"
                        onClick={() => {
                            setTab("about");
                        }}
                        active={_.isEqual(tab, "about")}
                    />
                </Card>
                <div style={{ padding: 15 }}>
                    <FormGroup label="Name">
                        <InputGroup
                            large
                            value={name}
                            onChange={(event) => {
                                setName(event.target.value);
                            }}
                        />
                    </FormGroup>
                    <FormGroup label="Description" className="margin-0">
                        <InputGroup
                            large
                            value={description}
                            onChange={(event) => {
                                setDescription(event.target.value);
                            }}
                        />
                    </FormGroup>
                </div>
            </DialogBody>
            <DialogFooter>
                <Button
                    loading={loading}
                    text="Save"
                    large
                    onClick={handleSaveMetadata}
                    intent={Intent.SUCCESS}
                    icon={faIcon({ icon: faCheck })}
                />
            </DialogFooter>
        </Dialog>
    );
}

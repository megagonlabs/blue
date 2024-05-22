import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import {
    Button,
    Card,
    Classes,
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
import SessionAgentsList from "./SessionAgentsList";
export default function SessionDetail({ isOpen, setIsSessionDetailOpen }) {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [allowQuickClose, setAllowQuickCloset] = useState(true);
    const sessionName = _.get(
        appState,
        ["session", "sessionDetail", sessionIdFocus, "name"],
        ""
    );
    const sessionDetail = _.get(
        appState,
        ["session", "sessionDetail", sessionIdFocus, "description"],
        ""
    );
    const [name, setName] = useState(sessionName);
    const [description, setDescription] = useState(sessionDetail);
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
                setAllowQuickCloset(true);
                setLoading(false);
                appActions.session.setSessionDetail([
                    { ...payload, id: sessionIdFocus },
                ]);
            })
            .catch((error) => {
                setAllowQuickCloset(true);
                setLoading(false);
            });
    };
    useEffect(() => {
        setName(sessionName);
        setDescription(sessionDetail);
    }, [sessionIdFocus, isOpen]);
    const [tab, setTab] = useState("about");
    return (
        <Dialog
            title={
                _.isEmpty(_.trim(sessionName)) ||
                _.isEqual(sessionName, sessionIdFocus) ? (
                    sessionIdFocus
                ) : (
                    <div>
                        {sessionName}&nbsp;
                        <span className={Classes.TEXT_MUTED}>
                            ({sessionIdFocus})
                        </span>
                    </div>
                )
            }
            canOutsideClickClose={allowQuickClose}
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
                    <Button
                        minimal
                        large
                        text="Members"
                        onClick={() => {
                            setTab("members");
                        }}
                        active={_.isEqual(tab, "members")}
                    />
                </Card>
                <div style={{ padding: 15 }}>
                    {_.isEqual(tab, "about") ? (
                        <>
                            <FormGroup label="Name">
                                <InputGroup
                                    large
                                    value={name}
                                    onChange={(event) => {
                                        setName(event.target.value);
                                        setAllowQuickCloset(false);
                                    }}
                                />
                            </FormGroup>
                            <FormGroup label="Description" className="margin-0">
                                <InputGroup
                                    large
                                    value={description}
                                    onChange={(event) => {
                                        setDescription(event.target.value);
                                        setAllowQuickCloset(false);
                                    }}
                                />
                            </FormGroup>
                        </>
                    ) : null}
                    {_.isEqual(tab, "members") ? <SessionAgentsList /> : null}
                </div>
            </DialogBody>
            {_.isEqual(tab, "about") ? (
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
            ) : null}
        </Dialog>
    );
}

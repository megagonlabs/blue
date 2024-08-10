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
import {
    faCheck,
    faCircleA,
    faSquareInfo,
    faUserGroup,
} from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useRef, useState } from "react";
import SessionAgentsList from "./SessionAgentsList";
import SessionMembersList from "./SessionMembersList";
export default function SessionDetail({ isOpen, setIsSessionDetailOpen }) {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const allowQuickClose = useRef(true);
    const sessionDetail = _.get(
        appState,
        ["session", "sessionDetail", sessionIdFocus],
        {}
    );
    const sessionName = _.get(sessionDetail, "name", "");
    const sessionDescription = _.get(sessionDetail, "description", "");
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
                appActions.session.setSessionDetail([
                    { ...sessionDetail, ...payload, id: sessionIdFocus },
                ]);
            })
            .catch(() => {
                allowQuickClose.current = true;
                setLoading(false);
            });
    };
    useEffect(() => {
        setName(sessionName);
        setDescription(sessionDescription);
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
            canOutsideClickClose={allowQuickClose.current}
            onClose={() => {
                if (loading) {
                    return;
                }
                setIsSessionDetailOpen(false);
            }}
            isOpen={isOpen}
            style={{ padding: 0 }}
        >
            <DialogBody className="dialog-body">
                <Card style={{ padding: "5px 15px", borderRadius: 0 }}>
                    <Button
                        icon={faIcon({ icon: faSquareInfo })}
                        minimal
                        large
                        text="About"
                        onClick={() => {
                            setTab("about");
                        }}
                        active={_.isEqual(tab, "about")}
                    />
                    <Button
                        icon={faIcon({ icon: faCircleA })}
                        minimal
                        large
                        text="Agents"
                        onClick={() => {
                            setTab("agents");
                        }}
                        active={_.isEqual(tab, "agents")}
                    />
                    <Button
                        icon={faIcon({ icon: faUserGroup })}
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
                        </>
                    ) : null}
                    {_.isEqual(tab, "agents") ? <SessionAgentsList /> : null}
                    {_.isEqual(tab, "members") ? <SessionMembersList /> : null}
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

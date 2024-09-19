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
    faMoneyBillsSimple,
    faSquareInfo,
    faUserGroup,
} from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useRef, useState } from "react";
import { AppToaster } from "../toaster";
import SessionAgentsList from "./details/SessionAgentsList";
import SessionBudget from "./details/SessionBudget";
import SessionMembersList from "./details/SessionMembersList";
export default function SessionDetail({ isOpen, setIsSessionDetailOpen }) {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const allowQuickClose = useRef(true);
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
                if (loading) return;
                setIsSessionDetailOpen(false);
            }}
            isOpen={isOpen}
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
                    <Button
                        icon={faIcon({ icon: faMoneyBillsSimple })}
                        minimal
                        large
                        text="Budget"
                        onClick={() => {
                            setTab("budget");
                        }}
                        active={_.isEqual(tab, "budget")}
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
                    {_.isEqual(tab, "budget") ? <SessionBudget /> : null}
                </div>
            </DialogBody>
            {_.includes(["about", "budget"], tab) ? (
                <DialogFooter>
                    {_.isEqual(tab, "about") ? (
                        <Button
                            disabled={_.isEmpty(_.trim(name))}
                            loading={loading}
                            text="Save"
                            large
                            onClick={handleSaveMetadata}
                            intent={Intent.SUCCESS}
                            icon={faIcon({ icon: faCheck })}
                        />
                    ) : null}
                    {_.isEqual(tab, "budget") ? (
                        <Button
                            loading={loading}
                            text="Save"
                            large
                            intent={Intent.SUCCESS}
                            icon={faIcon({ icon: faCheck })}
                        />
                    ) : null}
                </DialogFooter>
            ) : null}
        </Dialog>
    );
}

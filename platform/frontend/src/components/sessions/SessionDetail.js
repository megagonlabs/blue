import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { Button, Card, Classes, Dialog } from "@blueprintjs/core";
import {
    faCircleA,
    faMoneyBillsSimple,
    faSquareInfo,
    faUserGroup,
} from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useContext, useState } from "react";
import SessionAgentsList from "./details/SessionAgentsList";
import SessionBudget from "./details/SessionBudget";
import SessionMembersList from "./details/SessionMembersList";
import SessionMetadata from "./details/SessionMetadata";
export default function SessionDetail({ isOpen, setIsSessionDetailOpen }) {
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [allowQuickClose, setAllowQuickClose] = useState(true);
    const sessionDetails = _.get(
        appState,
        ["session", "sessionDetails", sessionIdFocus],
        {}
    );
    const sessionName = _.get(sessionDetails, "name", "");
    const [loading, setLoading] = useState(false);
    const [tab, setTab] = useState("about");
    return (
        <Dialog
            title={
                _.isEmpty(_.trim(sessionName)) ||
                _.isEqual(sessionName, sessionIdFocus) ? (
                    sessionIdFocus
                ) : (
                    <div className={Classes.TEXT_OVERFLOW_ELLIPSIS}>
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
        >
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
            {_.isEqual(tab, "about") ? (
                <SessionMetadata
                    setAllowQuickClose={setAllowQuickClose}
                    loading={loading}
                    setLoading={setLoading}
                />
            ) : null}
            {_.isEqual(tab, "agents") ? (
                <SessionAgentsList loading={loading} setLoading={setLoading} />
            ) : null}
            {_.isEqual(tab, "members") ? (
                <SessionMembersList loading={loading} setLoading={setLoading} />
            ) : null}
            {_.isEqual(tab, "budget") ? (
                <SessionBudget
                    setAllowQuickClose={setAllowQuickClose}
                    loading={loading}
                    setLoading={setLoading}
                />
            ) : null}
        </Dialog>
    );
}

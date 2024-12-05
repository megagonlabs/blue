import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { Button, ButtonGroup, Card, Classes, Dialog } from "@blueprintjs/core";
import {
    faCircleA,
    faFolderTree,
    faGear,
    faMoneyBillsSimple,
    faSquareInfo,
    faUserGroup,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import SessionAgentsList from "./details/SessionAgentsList";
import SessionBudget from "./details/SessionBudget";
import SessionData from "./details/SessionData";
import SessionMembersList from "./details/SessionMembersList";
import SessionMetadata from "./details/SessionMetadata";
import SessionSettings from "./details/SessionSettings";
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
    const TAB_BUTTONS = [
        { text: "About", icon: faSquareInfo, key: "about" },
        { text: "Agents", icon: faCircleA, key: "agents" },
        { text: "Members", icon: faUserGroup, key: "members" },
        { text: "Budget", icon: faMoneyBillsSimple, key: "budget" },
        { text: "Data", icon: faFolderTree, key: "data" },
        { text: "Settings", icon: faGear, key: "settings" },
    ];
    useEffect(() => {
        if (_.isNil(sessionIdFocus)) {
            setIsSessionDetailOpen(false);
            setTab("about");
        }
    }, [sessionIdFocus]); // eslint-disable-line react-hooks/exhaustive-deps
    return (
        <Dialog
            portalClassName="portal-overlay-z-index-36"
            title={
                _.isEmpty(_.trim(sessionName)) ||
                _.isEqual(sessionName, sessionIdFocus) ? (
                    sessionIdFocus
                ) : (
                    <div className={Classes.TEXT_OVERFLOW_ELLIPSIS}>
                        {sessionName}
                    </div>
                )
            }
            canOutsideClickClose={allowQuickClose}
            onClose={() => {
                if (loading) return;
                setIsSessionDetailOpen(false);
                setTab("about");
            }}
            isOpen={isOpen}
        >
            <Card
                style={{
                    padding: "5px 15px",
                    borderRadius: 0,
                    overflowX: "auto",
                    overscrollBehavior: "contain",
                }}
            >
                <ButtonGroup minimal large>
                    {TAB_BUTTONS.map((tabButton) => (
                        <Button
                            key={tabButton.key}
                            text={tabButton.text}
                            icon={faIcon({ icon: tabButton.icon })}
                            onClick={() => setTab(tabButton.key)}
                            active={_.isEqual(tab, tabButton.key)}
                        />
                    ))}
                </ButtonGroup>
            </Card>
            {_.isEqual(tab, "about") && (
                <SessionMetadata
                    setAllowQuickClose={setAllowQuickClose}
                    loading={loading}
                    setLoading={setLoading}
                />
            )}
            {_.isEqual(tab, "agents") && (
                <SessionAgentsList loading={loading} setLoading={setLoading} />
            )}
            {_.isEqual(tab, "members") && (
                <SessionMembersList loading={loading} setLoading={setLoading} />
            )}
            {_.isEqual(tab, "budget") && (
                <SessionBudget
                    setAllowQuickClose={setAllowQuickClose}
                    loading={loading}
                    setLoading={setLoading}
                />
            )}
            {_.isEqual(tab, "data") && <SessionData />}
            {_.isEqual(tab, "settings") && <SessionSettings />}
        </Dialog>
    );
}

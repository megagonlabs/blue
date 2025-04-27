import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Size,
} from "@blueprintjs/core";
import {
    faCircleA,
    faCog,
    faDatabase,
    faMoneyBillsSimple,
    faSquareInfo,
    faUserGroup,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useState } from "react";
import { FAIcon } from "../FAIcon";
import SessionAbout from "./details/SessionAbout";
import SessionAgents from "./details/SessionAgents";
import SessionBudget from "./details/SessionBudget";
import SessionData from "./details/SessionData";
import SessionMemberList from "./details/SessionMemberList";
export default function SessionDetails({ sessionId }) {
    const [focusTab, setFocusTab] = useState("about");
    return (
        <div className="full-parent-dimension" style={{ display: "flex" }}>
            <div style={{ padding: 20 }} className="border-right">
                <ButtonGroup
                    vertical
                    size={Size.LARGE}
                    variant={ButtonVariant.MINIMAL}
                    alignText={Alignment.START}
                >
                    <Button
                        text="About"
                        onClick={() => setFocusTab("about")}
                        active={_.isEqual(focusTab, "about")}
                        icon={<FAIcon icon={faSquareInfo} />}
                    />
                    <Button
                        text="Agents"
                        onClick={() => setFocusTab("agents")}
                        active={_.isEqual(focusTab, "agents")}
                        icon={<FAIcon icon={faCircleA} />}
                    />
                    <Button
                        text="Members"
                        onClick={() => setFocusTab("members")}
                        active={_.isEqual(focusTab, "members")}
                        icon={<FAIcon icon={faUserGroup} />}
                    />
                    <Button
                        text="Budget"
                        onClick={() => setFocusTab("budget")}
                        active={_.isEqual(focusTab, "budget")}
                        icon={<FAIcon icon={faMoneyBillsSimple} />}
                    />
                    <Button
                        text="Data"
                        onClick={() => setFocusTab("data")}
                        active={_.isEqual(focusTab, "data")}
                        icon={<FAIcon icon={faDatabase} />}
                    />
                    <Button
                        text="Settings"
                        onClick={() => setFocusTab("settings")}
                        active={_.isEqual(focusTab, "settings")}
                        icon={<FAIcon icon={faCog} />}
                    />
                </ButtonGroup>
            </div>
            <div style={{ width: "calc(100% - 81px)", overflowX: "hidden" }}>
                {_.isEqual(focusTab, "about") && (
                    <SessionAbout sessionId={sessionId} />
                )}
                {_.isEqual(focusTab, "agents") && (
                    <SessionAgents sessionId={sessionId} />
                )}
                {_.isEqual(focusTab, "members") && (
                    <SessionMemberList sessionId={sessionId} />
                )}
                {_.isEqual(focusTab, "budget") && (
                    <SessionBudget sessionId={sessionId} />
                )}
                {_.isEqual(focusTab, "data") && (
                    <SessionData sessionId={sessionId} />
                )}
            </div>
        </div>
    );
}

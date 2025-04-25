import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Size,
    Tooltip,
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
                >
                    <Tooltip placement="right" content="About">
                        <Button
                            onClick={() => setFocusTab("about")}
                            active={_.isEqual(focusTab, "about")}
                            icon={<FAIcon icon={faSquareInfo} />}
                        />
                    </Tooltip>
                    <Tooltip placement="right" content="Agents">
                        <Button
                            onClick={() => setFocusTab("agents")}
                            active={_.isEqual(focusTab, "agents")}
                            icon={<FAIcon icon={faCircleA} />}
                        />
                    </Tooltip>
                    <Tooltip placement="right" content="Members">
                        <Button
                            onClick={() => setFocusTab("members")}
                            active={_.isEqual(focusTab, "members")}
                            icon={<FAIcon icon={faUserGroup} />}
                        />
                    </Tooltip>
                    <Tooltip placement="right" content="Budget">
                        <Button
                            onClick={() => setFocusTab("budget")}
                            active={_.isEqual(focusTab, "budget")}
                            icon={<FAIcon icon={faMoneyBillsSimple} />}
                        />
                    </Tooltip>
                    <Tooltip placement="right" content="Data">
                        <Button
                            onClick={() => setFocusTab("data")}
                            active={_.isEqual(focusTab, "data")}
                            icon={<FAIcon icon={faDatabase} />}
                        />
                    </Tooltip>
                    <Tooltip placement="right" content="Settings">
                        <Button
                            onClick={() => setFocusTab("settings")}
                            active={_.isEqual(focusTab, "settings")}
                            icon={<FAIcon icon={faCog} />}
                        />
                    </Tooltip>
                </ButtonGroup>
            </div>
            <div style={{ width: "calc(100% - 81px)" }}>
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
            </div>
        </div>
    );
}

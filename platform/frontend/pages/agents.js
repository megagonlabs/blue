
import { AppContext } from "@/components/app-context";
import { H4, InputGroup, Button, ButtonGroup, H1 } from "@blueprintjs/core";
import { faIcon } from "@/components/icon";
import AgentList from "@/components/agents/AgentList";
import { AppToaster } from "@/components/toaster";
import { Card, Intent, NonIdealState } from "@blueprintjs/core";
import { faInboxIn, faMessages } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
export default function Agents() {
    const { appState, appActions } = useContext(AppContext);
    const [isSearchOptionOpen, setIsSearchOptionOpen] = useState(false);
    useEffect(() => {
    }, []);
    return (
        <>
            <div
                style={{
                    // position: "absolute",
                    top: 20,
                    left: 20,
                    height: "100%",
                    width: "100%",
                }}
            >
            <H4
                    className="margin-0"
                    style={{
                        lineHeight: "30px",
                        marginRight: 10,
                    }}
                >
                    Agents Registry (default)
            </H4>
            <AgentList />
            </div>
        </>
    );
}

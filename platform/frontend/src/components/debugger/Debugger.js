import {
    Button,
    ButtonGroup,
    Card,
    Divider,
    HTMLSelect,
    Tooltip,
} from "@blueprintjs/core";
import { faBan } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useContext, useState } from "react";
import { AppContext } from "../contexts/app-context";
import { faIcon } from "../icon";
export default function Debugger() {
    const { appState, appActions } = useContext(AppContext);
    const [focusMessageType, setFocusMessageType] = useState("all");
    const messages = _.get(appState, "debug.messages", []);
    return (
        <>
            <Card style={{ borderRadius: 0, padding: "5px 15px" }}>
                <ButtonGroup minimal>
                    <HTMLSelect minimal>
                        <option value="all">All</option>
                    </HTMLSelect>
                    <Tooltip minimal content="Clear all" placement="bottom">
                        <Button
                            onClick={appActions.debug.clearMessages}
                            icon={faIcon({
                                icon: faBan,
                                className: "fa-rotate-by",
                                style: { "--fa-rotate-angle": "90deg" },
                            })}
                        />
                    </Tooltip>
                </ButtonGroup>
            </Card>
            <div
                style={{
                    height: "calc(100% - 40px)",
                    overflowY: "auto",
                    overflowX: "hidden",
                    padding: 15,
                }}
            >
                {messages.map((message, index) => {
                    return (
                        <div key={index} style={{ whiteSpace: "pre-wrap" }}>
                            {JSON.stringify(message, null, 4)}
                            <Divider />
                        </div>
                    );
                })}
            </div>
        </>
    );
}

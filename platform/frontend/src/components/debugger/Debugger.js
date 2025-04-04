import { faIcon } from "@/components/icon";
import {
    Button,
    ButtonGroup,
    Divider,
    HTMLSelect,
    Tooltip,
} from "@blueprintjs/core";
import { faBan } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext } from "react";
import { AppContext } from "../contexts/app-context";
import JsonViewer from "../sessions/message/renderers/JsonViewer";
export default function Debugger() {
    const { appState, appActions } = useContext(AppContext);
    // const [focusMessageType, setFocusMessageType] = useState("all");
    const messages = _.get(appState, "debug.messages", []);
    return (
        <>
            <div
                className="border-bottom"
                style={{ borderRadius: 0, padding: "5px 15px" }}
            >
                <ButtonGroup variant="minimal" size="large">
                    <Tooltip
                        minimal
                        content="Clear debugger"
                        placement="bottom-start"
                    >
                        <Button
                            onClick={appActions.debug.clearMessages}
                            icon={faIcon({
                                icon: faBan,
                                className: "fa-rotate-by",
                                style: { "--fa-rotate-angle": "90deg" },
                            })}
                        />
                    </Tooltip>
                    <Divider />
                    <HTMLSelect large id="debugger-message-type" minimal>
                        <option value="all">All</option>
                    </HTMLSelect>
                </ButtonGroup>
            </div>
            <div
                style={{
                    height: "calc(100% - 50px)",
                    overflowX: "auto",
                    padding: 15,
                }}
            >
                {messages.map((message, index) => {
                    return (
                        <>
                            <JsonViewer
                                json={_.omit(message, ["type"])}
                                key={index}
                                collapsed={({ indexOrName }) => {
                                    return ["uischema", "schema"].includes(
                                        indexOrName
                                    );
                                }}
                            />
                            {index < _.size(messages) - 1 ? <Divider /> : null}
                        </>
                    );
                })}
            </div>
        </>
    );
}

import { useSocketStore } from "@/stores/socket-store";
import { Button, ButtonVariant, HTMLTable, Size } from "@blueprintjs/core";
import {
    faClipboard,
    faCopy,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import copy from "copy-to-clipboard";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "./FAIcon";
import withAutoSizer from "./hocs/withAutoSizer";
import { AppToaster } from "./toaster";
function NerdStats({ width, height }) {
    const { connectionId } = useSocketStore(
        useShallow((state) => ({
            connectionId: state.connectionId,
        }))
    );
    return (
        <div style={{ width, height }}>
            <div className="full-parent-dimension">
                <HTMLTable striped className="full-parent-width nerd-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Connection ID</td>
                            <td>
                                <Button
                                    size={Size.LARGE}
                                    variant={ButtonVariant.MINIMAL}
                                    endIcon={<FAIcon icon={faCopy} />}
                                    onClick={() => {
                                        copy(connectionId);
                                        AppToaster.show({
                                            icon: <FAIcon icon={faClipboard} />,
                                            message: "Copied Connection ID",
                                        });
                                    }}
                                    text={connectionId}
                                />
                            </td>
                        </tr>
                    </tbody>
                </HTMLTable>
            </div>
        </div>
    );
}
export default withAutoSizer(NerdStats);

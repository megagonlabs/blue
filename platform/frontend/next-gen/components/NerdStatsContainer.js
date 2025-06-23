import { useSocketStore } from "@/stores/socket-store";
import { HTMLTable, Size, Tag, Tooltip } from "@blueprintjs/core";
import {
    faClipboard,
    faCopy,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import copy from "copy-to-clipboard";
import { allEnv } from "next-runtime-env";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "./FAIcon";
import withAutoSizer from "./hocs/withAutoSizer";
import { AppToaster } from "./toaster";
const { NEXT_PUBLIC_GIT_LONG, NEXT_PUBLIC_GIT_BRANCH, NEXT_PUBLIC_GIT_SHORT } =
    allEnv();
function NerdStatsContainer({ width, height }) {
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
                            <td>Version</td>
                            <td>
                                <Tooltip content="Copy full SHA">
                                    <Tag
                                        minimal
                                        size={Size.LARGE}
                                        endIcon={<FAIcon icon={faCopy} />}
                                        onClick={() => {
                                            copy(NEXT_PUBLIC_GIT_LONG);
                                            AppToaster.show({
                                                icon: (
                                                    <FAIcon
                                                        icon={faClipboard}
                                                    />
                                                ),
                                                message: `Copied "${NEXT_PUBLIC_GIT_LONG}"`,
                                            });
                                        }}
                                    >
                                        {NEXT_PUBLIC_GIT_BRANCH}-
                                        {NEXT_PUBLIC_GIT_SHORT}
                                    </Tag>
                                </Tooltip>
                            </td>
                        </tr>
                        <tr>
                            <td>Connection ID</td>
                            <td>
                                <Tag
                                    minimal
                                    size={Size.LARGE}
                                    endIcon={<FAIcon icon={faCopy} />}
                                    onClick={() => {
                                        copy(connectionId);
                                        AppToaster.show({
                                            icon: <FAIcon icon={faClipboard} />,
                                            message: "Copied Connection ID",
                                        });
                                    }}
                                >
                                    {connectionId}
                                </Tag>
                            </td>
                        </tr>
                    </tbody>
                </HTMLTable>
            </div>
        </div>
    );
}
export default withAutoSizer(NerdStatsContainer);

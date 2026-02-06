import { useAppStore } from "@/stores/app-store";
import { useSocketStore } from "@/stores/socket-store";
import { Colors, HTMLTable, Size, Tag, Tooltip } from "@blueprintjs/core";
import {
    faClipboard,
    faCopy,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import copy from "copy-to-clipboard";
import { allEnv } from "next-runtime-env";
import { useRef } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { useShallow } from "zustand/react/shallow";
import { useToaster } from "./contexts/ToasterContext";
import { FAIcon } from "./FAIcon";
import withAutoSizer from "./hocs/withAutoSizer";
const { NEXT_PUBLIC_GIT_LONG, NEXT_PUBLIC_GIT_BRANCH, NEXT_PUBLIC_GIT_SHORT } =
    allEnv();
function NerdStatsContainer({ width, height }) {
    const { connectionId } = useSocketStore(
        useShallow((state) => ({
            connectionId: state.connectionId,
        }))
    );
    const darkMode = useAppStore((state) => state.dark_mode);
    const elementRef = useRef(null);
    const { appToaster } = useToaster();
    const copyConnectionId = () => {
        copy(connectionId);
        if (appToaster) {
            appToaster.show({
                icon: <FAIcon icon={faClipboard} />,
                message: "Copied Connection ID",
            });
        }
    };
    const copyVersion = () => {
        copy(NEXT_PUBLIC_GIT_LONG);
        appToaster.show({
            icon: <FAIcon icon={faClipboard} />,
            message: `Copied "${NEXT_PUBLIC_GIT_LONG}"`,
        });
    };
    return (
        <div
            ref={elementRef}
            style={{
                width,
                height,
                backgroundColor: darkMode ? Colors.BLACK : null,
            }}
        >
            <div
                className="full-parent-dimension"
                style={{ overflowY: "auto" }}
            >
                <AutoSizer>
                    {({ width: tableWidth }) => (
                        <HTMLTable
                            style={{ width: tableWidth }}
                            striped
                            className="table-header-sticky nerd-table"
                        >
                            <thead
                                style={{
                                    position: "sticky",
                                    top: 0,
                                    backgroundColor: darkMode
                                        ? Colors.BLACK
                                        : Colors.WHITE,
                                    zIndex: 1,
                                }}
                            >
                                <tr>
                                    <th className="border-bottom">Name</th>
                                    <th className="border-bottom">Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Version</td>
                                    <td>
                                        <Tooltip
                                            boundary={elementRef.current}
                                            placement="bottom"
                                            content="Copy full SHA"
                                        >
                                            <Tag
                                                minimal
                                                size={Size.LARGE}
                                                endIcon={
                                                    <FAIcon icon={faCopy} />
                                                }
                                                onClick={copyVersion}
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
                                            onClick={copyConnectionId}
                                        >
                                            {connectionId}
                                        </Tag>
                                    </td>
                                </tr>
                            </tbody>
                        </HTMLTable>
                    )}
                </AutoSizer>
            </div>
        </div>
    );
}
export default withAutoSizer(NerdStatsContainer);

import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import { Button, Tooltip } from "@blueprintjs/core";
import { faClipboard, faCopy } from "@fortawesome/pro-duotone-svg-icons";
import copy from "copy-to-clipboard";
export default function CopyDocJsonButton({
    docJson,
    copyMessage = "Copied JSON",
}) {
    return (
        <Tooltip
            usePortal={false}
            minimal
            placement="bottom-end"
            content="Copy JSON"
        >
            <Button
                minimal
                icon={faIcon({ icon: faCopy })}
                large
                onClick={() => {
                    copy(docJson);
                    AppToaster.show({
                        icon: faIcon({ icon: faClipboard }),
                        message: copyMessage,
                    });
                }}
            />
        </Tooltip>
    );
}

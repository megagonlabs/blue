import { FAIcon } from "@/components/FAIcon";
import { AppToaster } from "@/components/toaster";
import { Button, Size, Tooltip } from "@blueprintjs/core";
import {
    faClipboard,
    faCopy,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
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
                variant="minimal"
                icon={<FAIcon icon={faCopy} />}
                size={Size.LARGE}
                onClick={() => {
                    copy(docJson);
                    AppToaster.show({
                        icon: <FAIcon icon={faClipboard} />,
                        message: copyMessage,
                    });
                }}
            />
        </Tooltip>
    );
}

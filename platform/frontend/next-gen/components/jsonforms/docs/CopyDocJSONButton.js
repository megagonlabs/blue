import { useToaster } from "@/components/contexts/ToasterContext";
import { FAIcon } from "@/components/FAIcon";
import { Button, ButtonVariant, Size, Tooltip } from "@blueprintjs/core";
import {
    faClipboard,
    faCopy,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import copy from "copy-to-clipboard";
export default function CopyDocJSONButton({
    docJson,
    copyMessage = "Copied JSON",
}) {
    const { appToaster } = useToaster();
    return (
        <Tooltip usePortal={false} placement="bottom-end" content="Copy JSON">
            <Button
                variant={ButtonVariant.MINIMAL}
                icon={<FAIcon icon={faCopy} />}
                size={Size.LARGE}
                onClick={() => {
                    copy(docJson);
                    appToaster.show({
                        icon: <FAIcon icon={faClipboard} />,
                        message: copyMessage,
                    });
                }}
            />
        </Tooltip>
    );
}

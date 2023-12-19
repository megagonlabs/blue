import { faIcon } from "@/components/icon";
import {
    Button,
    ControlGroup,
    Dialog,
    DialogBody,
    H3,
    InputGroup,
    Intent,
    Tag,
} from "@blueprintjs/core";
import { faNetworkWired } from "@fortawesome/pro-duotone-svg-icons";
import { useState } from "react";
export default function Index() {
    const [server, setServer] = useState("");
    return (
        <Dialog isCloseButtonShown={false} isOpen>
            <DialogBody>
                <H3>Connect to websocket:</H3>
                <ControlGroup fill>
                    <InputGroup
                        leftElement={<Tag minimal>ws://</Tag>}
                        large
                        value={server}
                        onChange={(event) => setServer(event.target.value)}
                    />
                </ControlGroup>
                <Button
                    icon={faIcon({ icon: faNetworkWired })}
                    style={{ marginTop: 10 }}
                    large
                    intent={Intent.PRIMARY}
                    text="Connect"
                />
            </DialogBody>
        </Dialog>
    );
}

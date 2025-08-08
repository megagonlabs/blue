import {
    Button,
    ButtonVariant,
    Checkbox,
    EntityTitle,
    H1,
    Overlay2,
    Size,
} from "@blueprintjs/core";
import {
    faSparkles,
    faXmarkLarge,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useState } from "react";
import { FAIcon } from "../FAIcon";
export default function ReleaseNotes() {
    const [isOpen, setIsOpen] = useState(false);
    return (
        <Overlay2
            enforceFocus={false}
            transitionDuration={0}
            isOpen={isOpen}
            usePortal={false}
            onClose={() => {
                setIsOpen(false);
            }}
            canOutsideClickClose={false}
        >
            <div
                className="custom-card center-center"
                style={{
                    width: 800,
                    padding: 20,
                    overflowY: "auto",
                    height: "calc(100% - 40px)",
                    maxWidth: "calc(100% - 40px)",
                }}
            >
                <Button
                    onClick={() => {
                        setIsOpen(false);
                    }}
                    size={Size.LARGE}
                    variant={ButtonVariant.MINIMAL}
                    style={{ position: "absolute", top: 20, right: 20 }}
                    icon={<FAIcon icon={faXmarkLarge} />}
                />
                <EntityTitle
                    heading={H1}
                    title="Release Notes"
                    icon={<FAIcon icon={faSparkles} size={30} />}
                />
                message body
                <Checkbox
                    style={{ marginBottom: 0, marginTop: 10 }}
                    label="Don't show this again"
                />
            </div>
        </Overlay2>
    );
}

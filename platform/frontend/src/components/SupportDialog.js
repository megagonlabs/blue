import build from "@/build.preval";
import {
    Classes,
    Dialog,
    DialogBody,
    H3,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { faCopyright } from "@fortawesome/pro-duotone-svg-icons";
import { faIcon } from "./icon";
export default function SupportDialog({ isOpen, setIsSupportDialogOpen }) {
    const { short, long, branch } = build;
    return (
        <Dialog onClose={() => setIsSupportDialogOpen(false)} isOpen={isOpen}>
            <DialogBody>
                <H3>Blue</H3>
                <div
                    className={Classes.TEXT_LARGE}
                    style={{ marginBottom: 20 }}
                >
                    Orchestrating data & tasks for smarter insights.
                </div>
                <Tooltip placement="right" content={long}>
                    <Tag large>
                        {branch} / {short}
                    </Tag>
                </Tooltip>
                <div style={{ marginTop: 10 }}>
                    {faIcon({ icon: faCopyright })} {new Date().getFullYear()}{" "}
                    Megagon Labs. All rights reserved.
                </div>
            </DialogBody>
        </Dialog>
    );
}

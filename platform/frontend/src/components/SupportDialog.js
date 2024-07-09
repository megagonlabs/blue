import {
    Classes,
    Dialog,
    DialogBody,
    H3,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
export default function SupportDialog({ isOpen, setIsSupportDialogOpen }) {
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
                <Tooltip
                    placement="right"
                    content={process.env.NEXT_PUBLIC_GIT_LONG}
                >
                    <Tag large>
                        {process.env.NEXT_PUBLIC_GIT_BRANCH}-
                        {process.env.NEXT_PUBLIC_GIT_SHORT}
                    </Tag>
                </Tooltip>
            </DialogBody>
        </Dialog>
    );
}

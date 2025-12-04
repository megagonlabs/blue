import { useFileStore } from "@/stores/file-store";
import { useSocketStore } from "@/stores/socket-store";
import { H3 } from "@blueprintjs/core";
import { useCallback } from "react";
import { useShallow } from "zustand/react/shallow";
import { MAX_FILE_SIZE } from "../constants";
import DropZone from "../fileupload/DropZone";
import Files from "../fileupload/Files";
import { generateId } from "../fileupload/helper";
export default function AddSessionFile({ sessionId }) {
    const { addFile } = useFileStore(
        useShallow((state) => ({ addFile: state.addFile }))
    );
    const handleFilesAdd = useCallback((newFiles) => {
        const newItems = newFiles.map((file) => {
            const isLargeFile = file.size > MAX_FILE_SIZE;
            return {
                id: generateId(),
                file,
                progress: 0,
                status: isLargeFile ? "ERROR" : "PENDING",
                error: isLargeFile ? "File exceeds 50 MB limit" : null,
            };
        });
        addFile(sessionId, newItems);
    }, []);
    const { sendMessage } = useSocketStore(
        useShallow((state) => ({ sendMessage: state.sendMessage }))
    );
    const uploadCallback = (file) => {
        sendMessage(
            JSON.stringify({
                type: "USER_SESSION_MESSAGE",
                session_id: sessionId,
                message: file,
            })
        );
    };
    return (
        <div
            className="full-parent-dimension"
            style={{ overflow: "auto", padding: 20 }}
        >
            <H3 style={{ marginBottom: 20 }}>Files</H3>
            <DropZone onFilesAdded={handleFilesAdd} bucketId={sessionId} />
            <div style={{ marginTop: 20 }}>
                <Files
                    bucketId={sessionId}
                    uploadCallback={uploadCallback}
                    uploadUrl={`/sessions/session/${sessionId}/upload`}
                />
            </div>
        </div>
    );
}

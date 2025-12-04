import { useFileStore } from "@/stores/file-store";
import { Colors, NonIdealState } from "@blueprintjs/core";
import {
    faArrowDownToBracket,
    faUpload,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useCallback, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../FAIcon";
export default function DropZone({ onFilesAdded, bucketId }) {
    const { files } = useFileStore(
        useShallow((state) => ({ files: state.files }))
    );
    const disabled = _.get(files, [bucketId, "uploading"], false);
    const [isDragging, setIsDragging] = useState(false);
    const inputRef = useRef(null);
    const handleDragEnter = useCallback(
        (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (!disabled) {
                setIsDragging(true);
            }
        },
        [disabled]
    );
    const handleDragLeave = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    }, []);
    const handleDragOver = useCallback(
        (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (!disabled) {
                setIsDragging(true);
            }
        },
        [disabled]
    );
    const handleDrop = useCallback(
        (e) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDragging(false);
            if (disabled) return;
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                onFilesAdded(Array.from(e.dataTransfer.files));
            }
        },
        [onFilesAdded, disabled]
    );
    const handleFileInputChange = useCallback(
        (e) => {
            if (e.target.files && e.target.files.length > 0) {
                onFilesAdded(Array.from(e.target.files));
            }
            if (inputRef.current) {
                inputRef.current.value = "";
            }
        },
        [onFilesAdded]
    );
    const onButtonClick = () => {
        inputRef.current?.click();
    };
    return (
        <div
            className="custom-card"
            style={{
                height: 200,
                cursor: disabled ? "not-allowed" : "pointer",
                borderWidth: "2px",
                borderStyle: "dashed",
                borderColor: isDragging ? Colors.BLUE3 : null,
                opacity: disabled ? 0.5 : 1,
            }}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={disabled ? null : onButtonClick}
        >
            <NonIdealState
                icon={
                    <FAIcon
                        icon={isDragging ? faArrowDownToBracket : faUpload}
                        size={50}
                        style={{ color: isDragging ? Colors.BLUE3 : null }}
                    />
                }
                title={
                    isDragging
                        ? "Drop files here"
                        : "Drag & drop files or click to browse"
                }
                description="Support for multiple files upload; images and documents (max 50 MB per file)."
            />
            <input
                ref={inputRef}
                type="file"
                multiple
                className="hidden"
                onChange={handleFileInputChange}
                disabled={disabled}
            />
        </div>
    );
}

import { useFileStore } from "@/stores/file-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Card,
    CardList,
    Classes,
    EntityTitle,
    Intent,
    ProgressBar,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faCloudArrowUp,
    faFile,
    faFilePdf,
    faImage,
    faMusic,
    faTrash,
    faVideo,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useShallow } from "zustand/react/shallow";
import { EMPTY_ARRAY, FILE_UPLOAD_STATUS } from "../constants";
import { FAIcon } from "../FAIcon";
import { calculateBytes } from "./helper";
export default function Files({ bucketId, uploadCallback, uploadUrl }) {
    const { files, removeFile, clearCompleted, startUpload } = useFileStore(
        useShallow((state) => ({
            files: state.files,
            removeFile: state.removeFile,
            clearCompleted: state.clearCompleted,
            startUpload: state.startUpload,
        }))
    );
    const bucketFiles = _.get(files, [bucketId, "files"], EMPTY_ARRAY);
    const isUploading = _.get(files, [bucketId, "uploading"], false);
    const completedFiles = _.size(
        bucketFiles.filter((f) => _.isEqual(f.status, "COMPLETED"))
    );
    const getFileIcon = (item) => {
        if (item.file.type.startsWith("image/")) return faImage;
        if (item.file.type.startsWith("video/")) return faVideo;
        if (item.file.type.startsWith("audio/")) return faMusic;
        if (item.file.type.includes("pdf")) return faFilePdf;
        return faFile; // default
    };
    if (_.isEmpty(bucketFiles)) return null;
    return (
        <div>
            <div style={{ marginBottom: 20, textAlign: Alignment.END }}>
                <ButtonGroup size={Size.LARGE}>
                    <Button
                        variant={ButtonVariant.MINIMAL}
                        text="Clear completed"
                        disabled={_.isEqual(completedFiles, 0)}
                        onClick={() => clearCompleted(bucketId)}
                    />
                    <Button
                        intent={Intent.PRIMARY}
                        text="Upload"
                        icon={<FAIcon icon={faCloudArrowUp} />}
                        loading={isUploading}
                        onClick={() =>
                            startUpload(bucketId, uploadUrl, uploadCallback)
                        }
                    />
                </ButtonGroup>
            </div>
            <CardList>
                {bucketFiles.map((item) => {
                    const status = item.status;
                    const isUploaded = _.isEqual(item.progress, 1);
                    return (
                        <Card
                            key={item.id}
                            interactive
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 20,
                                padding: "10px 20px",
                            }}
                        >
                            <EntityTitle
                                fill
                                ellipsize
                                title={
                                    <div
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 10,
                                        }}
                                    >
                                        <div
                                            className={classNames(
                                                Classes.TEXT_OVERFLOW_ELLIPSIS
                                            )}
                                        >
                                            {item.file.name}
                                        </div>
                                        <div
                                            style={{ flex: " 0 0 auto" }}
                                            className={Classes.TEXT_DISABLED}
                                        >
                                            {calculateBytes(item.file.size)}
                                        </div>
                                    </div>
                                }
                                subtitle={
                                    <ProgressBar
                                        style={{ marginTop: 8 }}
                                        value={item.progress}
                                        intent={
                                            isUploaded
                                                ? Intent.SUCCESS
                                                : Intent.PRIMARY
                                        }
                                        stripes={!isUploaded}
                                        animate={!isUploaded}
                                    />
                                }
                                icon={
                                    <FAIcon
                                        style={{
                                            marginRight: 12,
                                            marginTop: 6.5,
                                        }}
                                        size={25}
                                        icon={getFileIcon(item)}
                                    />
                                }
                                tags={
                                    <Tag
                                        minimal
                                        intent={_.get(
                                            FILE_UPLOAD_STATUS,
                                            [status, "intent"],
                                            null
                                        )}
                                    >
                                        {_.get(
                                            FILE_UPLOAD_STATUS,
                                            [status, "text"],
                                            "-"
                                        )}
                                    </Tag>
                                }
                            />
                            {status !== "COMPLETED" && (
                                <Tooltip content="Remove file">
                                    <Button
                                        intent={Intent.DANGER}
                                        icon={<FAIcon icon={faTrash} />}
                                        variant={ButtonVariant.MINIMAL}
                                        disabled={isUploading}
                                        onClick={() =>
                                            removeFile(bucketId, item.id)
                                        }
                                    />
                                </Tooltip>
                            )}
                        </Card>
                    );
                })}
            </CardList>
        </div>
    );
}

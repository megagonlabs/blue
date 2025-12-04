import { EMPTY_ARRAY, EMPTY_OBJECT } from "@/components/constants";
import axios from "axios";
import _ from "lodash";
import { create } from "zustand";
const uploadFileReal = async (item, updateFileState, uploadUrl) => {
    updateFileState(item.id, { status: "UPLOADING" });
    const formData = new FormData();
    formData.append("file", item.file);
    try {
        const response = await axios.post(uploadUrl, formData, {
            onUploadProgress: (progressEvent_1) => {
                const total = progressEvent_1.total || item.file.size;
                const progress = progressEvent_1.loaded / total;
                updateFileState(item.id, { progress });
            },
        });
        updateFileState(item.id, {
            status: "COMPLETED",
            progress: 1,
        });
        return _.get(response, "data.result", EMPTY_OBJECT);
    } catch (error) {
        console.error("Upload error:", error);
        const errorMsg =
            error.response?.data?.detail || error.message || "Upload failed";
        updateFileState(item.id, {
            status: "ERROR",
            error: errorMsg,
        });
        throw error;
    }
};
export const useFileStore = create((set, get) => ({
    files: {},
    addFile: (bucketId, items) => {
        const { files } = get();
        let newFiles = _.cloneDeep(files);
        let bucketFiles = _.cloneDeep(
            _.get(files, [bucketId, "files"], EMPTY_ARRAY)
        );
        bucketFiles = _.concat(bucketFiles, items);
        _.set(newFiles, [bucketId, "files"], bucketFiles);
        set({ files: newFiles });
    },
    removeFile: (bucketId, fileId) => {
        const { files } = get();
        let newFiles = _.cloneDeep(files);
        let bucketFiles = _.cloneDeep(
            _.get(files, [bucketId, "files"], EMPTY_ARRAY)
        );
        _.remove(bucketFiles, (file) => _.isEqual(file.id, fileId));
        _.set(newFiles, [bucketId, "files"], bucketFiles);
        set({ files: newFiles });
    },
    clearCompleted: (bucketId) => {
        set((state) => {
            const bucket = state.files[bucketId];
            if (!bucket) return state;
            return {
                files: {
                    ...state.files,
                    [bucketId]: {
                        ...bucket,
                        files: bucket.files.filter(
                            (f) => !_.isEqual(f.status, "COMPLETED")
                        ),
                    },
                },
            };
        });
    },
    updateFile: (bucketId, fileId, updates) => {
        set((state) => {
            const bucket = state.files[bucketId];
            if (!bucket) return state;
            const updatedFiles = bucket.files.map((f) =>
                _.isEqual(f.id, fileId) ? { ...f, ...updates } : f
            );
            return {
                files: {
                    ...state.files,
                    [bucketId]: { ...bucket, files: updatedFiles },
                },
            };
        });
    },
    startUpload: async (bucketId, uploadUrl, uploadCallback) => {
        set((state) => {
            const bucket = state.files[bucketId];
            if (!bucket) return state;
            return {
                files: {
                    ...state.files,
                    [bucketId]: { ...bucket, uploading: true },
                },
            };
        });
        const { files, updateFile } = get();
        const bucket = files[bucketId];
        if (!bucket) return;
        // process pending files
        const pendingFiles = bucket.files.filter((f) =>
            _.includes(["PENDING", "ERROR"], f.status)
        );
        if (_.isEmpty(pendingFiles)) {
            set((state) => {
                const bucket = state.files[bucketId];
                return {
                    files: {
                        ...state.files,
                        [bucketId]: { ...bucket, uploading: false },
                    },
                };
            });
            return;
        }
        // concurrent queue limit
        const CONCURRENCY = 2;
        const queue = [...pendingFiles];
        let activeCount = 0;
        // helper for updating state
        const updateBucketFile = (fileId, updates) =>
            updateFile(bucketId, fileId, updates);
        await new Promise((resolve) => {
            const processNext = () => {
                if (_.isEmpty(queue) && _.isEqual(activeCount, 0)) {
                    resolve();
                    return;
                }
                while (queue.length > 0 && activeCount < CONCURRENCY) {
                    const item = queue.shift();
                    activeCount++;
                    uploadFileReal(item, updateBucketFile, uploadUrl)
                        .then((response) => {
                            if (_.isFunction(uploadCallback)) {
                                uploadCallback(response);
                            }
                        })
                        .catch(() => {})
                        .finally(() => {
                            activeCount--;
                            processNext();
                        });
                }
            };
            processNext();
        });
        set((state) => {
            const bucket = state.files[bucketId];
            if (!bucket) return state;
            return {
                files: {
                    ...state.files,
                    [bucketId]: { ...bucket, uploading: false },
                },
            };
        });
    },
}));

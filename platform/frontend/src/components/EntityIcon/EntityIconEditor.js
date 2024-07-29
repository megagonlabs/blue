import {
    Button,
    ButtonGroup,
    Card,
    Collapse,
    ControlGroup,
    Dialog,
    DialogBody,
    DialogFooter,
    FileInput,
    Intent,
} from "@blueprintjs/core";
import {
    faArrowsToCircle,
    faCaretDown,
    faCaretUp,
    faCheck,
    faFaceViewfinder,
    faIcons,
    faImage,
    faTrash,
} from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useEffect, useRef, useState } from "react";
import ReactCrop, {
    centerCrop,
    convertToPixelCrop,
    makeAspectCrop,
} from "react-image-crop";
import "react-image-crop/dist/ReactCrop.css";
import { useDebounceEffect } from "../hooks/useDebounceEffect";
import { faIcon } from "../icon";
import RegistryCard from "../registry/RegistryCard";
import { canvasPreview } from "./canvasPreview";
import IconPicker from "./IconPicker";
export default function EntityIconEditor({
    isOpen,
    setIsIconEditorOpen,
    entity,
    updateEntity,
}) {
    const [extra, setExtra] = useState(null);
    useEffect(() => {
        const { type, properties } = entity;
        let temp = null;
        if (_.isEqual(type, "agent")) {
            temp = properties.image;
        } else if (_.isEqual(type, "data")) {
            temp = `${properties.connection.protocol}://${properties.connection.host}:${properties.connection.port}`;
        }
        setExtra(temp);
    }, [entity]);
    const [tab, setTab] = useState("image");
    const [crop, setCrop] = useState(null);
    const [completedCrop, setCompletedCrop] = useState(null);
    const [imgSrc, setImgSrc] = useState("");
    const onSelectFile = (event) => {
        if (event.target.files && event.target.files.length > 0) {
            setCrop(null); // Makes crop preview update between images.
            const reader = new FileReader();
            reader.addEventListener("load", () => {
                setImgSrc(reader.result?.toString() || "");
            });
            setFileName(event.target.files[0].name);
            reader.readAsDataURL(event.target.files[0]);
        }
    };
    const [fileName, setFileName] = useState("Choose file...");
    const imgRef = useRef(null);
    const previewCanvasRef = useRef(null);
    const centerAspectCrop = (
        mediaWidth,
        mediaHeight,
        aspect = 1,
        cropWidth = 100,
        cropHeight = 100
    ) => {
        return centerCrop(
            makeAspectCrop(
                { unit: "%", width: cropWidth, height: cropHeight },
                aspect,
                mediaWidth,
                mediaHeight
            ),
            mediaWidth,
            mediaHeight
        );
    };
    const loadingRef = useRef(false);
    const readFileAsDataURL = async (file) => {
        loadingRef.current = true;
        let result_base64 = await new Promise((resolve) => {
            let fileReader = new FileReader();
            fileReader.onload = (e) => resolve(fileReader.result);
            fileReader.readAsDataURL(file);
        });
        loadingRef.current = false;
        return result_base64;
    };
    const centerCropManually = () => {
        const centerCropArea = centerAspectCrop(
            imgRef.current.width,
            imgRef.current.height,
            1,
            crop.width,
            crop.height
        );
        setCrop(centerCropArea);
        setCompletedCrop(
            convertToPixelCrop(
                centerCropArea,
                imgRef.current.width,
                imgRef.current.height
            )
        );
    };
    const applyIcon = async () => {
        if (_.isEqual(tab, "image")) {
            const image = imgRef.current;
            const previewCanvas = previewCanvasRef.current;
            if (!image || !previewCanvas || !completedCrop) {
                throw new Error("Crop canvas does not exist");
            }

            // This will size relative to the uploaded image
            // size. If you want to size according to what they
            // are looking at on screen, remove scaleX + scaleY
            const scaleX = image.naturalWidth / image.width;
            const scaleY = image.naturalHeight / image.height;

            const offscreen = new OffscreenCanvas(
                completedCrop.width * scaleX,
                completedCrop.height * scaleY
            );
            const ctx = offscreen.getContext("2d");
            if (!ctx) {
                throw new Error("No 2d context");
            }

            ctx.drawImage(
                previewCanvas,
                0,
                0,
                previewCanvas.width,
                previewCanvas.height,
                0,
                0,
                offscreen.width,
                offscreen.height
            );

            // You might want { type: "image/jpeg", quality: <0 to 1> } to
            // reduce image size
            const blob = await offscreen.convertToBlob({
                type: "image/jpeg",
                quality: 1,
            });
            const dataURL = await readFileAsDataURL(blob);
            updateEntity({ path: "icon", value: dataURL });
            closeEditor();
        }
    };
    const [icon, setIcon] = useState(null);
    const [color, setColor] = useState(null);
    const closeEditor = () => {
        if (loadingRef.current) {
            return;
        }
        setIsIconEditorOpen(false);
        setShowPreview(false);
        setCrop(null);
        setImgSrc("");
        setFileName("Choose file...");
    };
    useDebounceEffect(
        async () => {
            if (
                completedCrop?.width &&
                completedCrop?.height &&
                imgRef.current &&
                previewCanvasRef.current
            ) {
                // We use canvasPreview as it's much faster than imgPreview.
                canvasPreview(
                    imgRef.current,
                    previewCanvasRef.current,
                    completedCrop
                );
            }
        },
        100,
        [completedCrop]
    );
    useEffect(() => {
        setImgSrc(_.isEmpty(entity.icon) ? "" : entity.icon);
    }, [entity, isOpen]);
    const onImageLoad = (event) => {
        const { width, height } = event.currentTarget;
        setCrop(centerAspectCrop(width, height));
    };
    const [showPreview, setShowPreview] = useState(false);
    return (
        <Dialog
            canEscapeKeyClose={false}
            canOutsideClickClose={false}
            onClose={closeEditor}
            title="Entity Icon"
            isOpen={isOpen}
        >
            <DialogBody className="dialog-body">
                <Card style={{ padding: "5px 15px", borderRadius: 0 }}>
                    <Button
                        disabled
                        icon={faIcon({ icon: faIcons })}
                        minimal
                        large
                        text="Icon"
                        onClick={() => {
                            setTab("icon");
                        }}
                        active={_.isEqual(tab, "icon")}
                    />
                    <Button
                        icon={faIcon({ icon: faImage })}
                        minimal
                        large
                        text="Image"
                        onClick={() => {
                            setTab("image");
                        }}
                        active={_.isEqual(tab, "image")}
                    />
                </Card>
                <div style={{ padding: 15 }}>
                    {_.isEqual(tab, "image") ? (
                        <div>
                            <ControlGroup fill>
                                <FileInput
                                    large
                                    inputProps={{ accept: "image/*" }}
                                    style={{ maxWidth: 216.57 }}
                                    text={fileName}
                                    onInputChange={onSelectFile}
                                />
                                {!!imgSrc && (
                                    <>
                                        <Button
                                            text="Preview"
                                            fill
                                            minimal
                                            onClick={() =>
                                                setShowPreview(!showPreview)
                                            }
                                            icon={faIcon({
                                                icon: faFaceViewfinder,
                                            })}
                                            rightIcon={faIcon({
                                                icon: showPreview
                                                    ? faCaretUp
                                                    : faCaretDown,
                                            })}
                                        />

                                        <Button
                                            text="Center crop"
                                            fill
                                            minimal
                                            icon={faIcon({
                                                icon: faArrowsToCircle,
                                            })}
                                            onClick={centerCropManually}
                                        />
                                    </>
                                )}
                            </ControlGroup>
                            {!!imgSrc && (
                                <>
                                    <Collapse
                                        keepChildrenMounted
                                        isOpen={showPreview}
                                    >
                                        <Card
                                            style={{
                                                boxShadow: "none",
                                                padding: 20,
                                                width: 300,
                                                marginTop: 15,
                                            }}
                                        >
                                            <RegistryCard
                                                title={entity.name}
                                                description={entity.description}
                                                extra={extra}
                                                container={entity.container}
                                                previewIcon={
                                                    <canvas
                                                        ref={previewCanvasRef}
                                                        style={{
                                                            objectFit:
                                                                "contain",
                                                            width: 40,
                                                            height: 40,
                                                        }}
                                                    />
                                                }
                                            />
                                        </Card>
                                    </Collapse>
                                    <ReactCrop
                                        renderSelectionAddon={() => {
                                            if (_.isEmpty(entity.icon)) {
                                                return null;
                                            }
                                            return (
                                                <div
                                                    style={{
                                                        position: "relative",
                                                    }}
                                                >
                                                    <Button
                                                        style={{
                                                            position:
                                                                "absolute",
                                                            right: 2,
                                                            top: 2,
                                                        }}
                                                        intent={Intent.DANGER}
                                                        large
                                                        onClick={() => {
                                                            updateEntity({
                                                                path: "icon",
                                                                value: null,
                                                            });
                                                            closeEditor();
                                                        }}
                                                        icon={faIcon({
                                                            icon: faTrash,
                                                        })}
                                                    />
                                                </div>
                                            );
                                        }}
                                        style={{ marginTop: 15 }}
                                        keepSelection
                                        crop={crop}
                                        onChange={(_, percentCrop) => {
                                            setCrop(percentCrop);
                                        }}
                                        onComplete={(crop, percentCrop) => {
                                            setCompletedCrop(
                                                convertToPixelCrop(
                                                    percentCrop,
                                                    imgRef.current.width,
                                                    imgRef.current.height
                                                )
                                            );
                                        }}
                                        aspect={1}
                                        minWidth={80}
                                        minHeight={80}
                                    >
                                        <img
                                            ref={imgRef}
                                            alt="Crop me"
                                            src={imgSrc}
                                            onLoad={onImageLoad}
                                        />
                                    </ReactCrop>
                                </>
                            )}
                        </div>
                    ) : null}
                    {_.isEqual(tab, "icon") ? (
                        <IconPicker
                            icon={icon}
                            setIcon={setIcon}
                            color={color}
                            setColor={setColor}
                        />
                    ) : null}
                </div>
            </DialogBody>
            <DialogFooter>
                <ButtonGroup>
                    <Button
                        disabled={
                            !imgRef.current ||
                            !previewCanvasRef.current ||
                            !completedCrop
                        }
                        onClick={applyIcon}
                        text={`Apply ${tab}`}
                        large
                        icon={faIcon({ icon: faCheck })}
                    />
                </ButtonGroup>
            </DialogFooter>
        </Dialog>
    );
}

import {
    Button,
    Card,
    Collapse,
    Colors,
    ControlGroup,
    Dialog,
    DialogBody,
    DialogFooter,
    FileInput,
    H5,
    Intent,
    Tag,
} from "@blueprintjs/core";
import {
    faArrowsToCircle,
    faCaretDown,
    faCaretUp,
    faCheck,
    faFaceViewfinder,
    faImage,
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
import { canvasPreview } from "./canvasPreview";
export default function EntityIconEditor({
    isOpen,
    setIsIconEditorOpen,
    entity,
    updateEntity,
}) {
    const [extra, setExtra] = useState(null);
    const containerStatus = _.get(entity, "container.status", "not exist");
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
            reader.addEventListener("load", () =>
                setImgSrc(reader.result?.toString() || "")
            );
            reader.readAsDataURL(event.target.files[0]);
        }
    };
    const imgRef = useRef(null);
    const previewCanvasRef = useRef(null);
    const centerAspectCrop = (
        mediaWidth,
        mediaHeight,
        aspect = 1,
        cropWidth = 90,
        cropHeight = 90
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
                type: "image/png",
            });
            const dataURL = await readFileAsDataURL(blob);
            updateEntity({ path: "icon", value: dataURL });
            closeEditor();
        }
    };
    const closeEditor = () => {
        if (loadingRef.current) {
            return;
        }
        setIsIconEditorOpen(false);
        setImgSrc("");
        setShowPreview(false);
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
    const onImageLoad = (event) => {
        const { width, height } = event.currentTarget;
        setCrop(centerAspectCrop(width, height));
    };
    const [showPreview, setShowPreview] = useState(false);
    return (
        <Dialog onClose={closeEditor} title="Entity Icon" isOpen={isOpen}>
            <DialogBody className="padding-0">
                <Card style={{ padding: "5px 15px", borderRadius: 0 }}>
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
                                    inputProps={{ accept: "image/*" }}
                                    style={{ maxWidth: 216.57 }}
                                    text="Choose file..."
                                    onInputChange={onSelectFile}
                                />
                                {!!imgSrc && (
                                    <>
                                        <Button
                                            minimal
                                            onClick={() =>
                                                setShowPreview(!showPreview)
                                            }
                                            icon={faIcon({
                                                icon: faFaceViewfinder,
                                            })}
                                            text="Preview"
                                            rightIcon={faIcon({
                                                icon: showPreview
                                                    ? faCaretUp
                                                    : faCaretDown,
                                            })}
                                        />
                                        <Button
                                            minimal
                                            icon={faIcon({
                                                icon: faArrowsToCircle,
                                            })}
                                            text="Center crop"
                                            onClick={() => {
                                                const centerCrop =
                                                    centerAspectCrop(
                                                        imgRef.current.width,
                                                        imgRef.current.height,
                                                        1,
                                                        crop.width,
                                                        crop.height
                                                    );
                                                setCrop(centerCrop);
                                                setCompletedCrop(
                                                    convertToPixelCrop(
                                                        centerCrop,
                                                        imgRef.current.width,
                                                        imgRef.current.height
                                                    )
                                                );
                                            }}
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
                                                padding: 15,
                                                width: 300,
                                                marginTop: 15,
                                            }}
                                        >
                                            <Card
                                                style={{
                                                    position: "relative",
                                                    backgroundColor:
                                                        Colors.LIGHT_GRAY5,
                                                }}
                                            >
                                                <Card
                                                    style={{
                                                        overflow: "hidden",
                                                        position: "absolute",
                                                        left: 20,
                                                        top: 20,
                                                        padding: 0,
                                                        height: 40,
                                                        width: 40,
                                                        display: "flex",
                                                        justifyContent:
                                                            "center",
                                                        alignItems: "center",
                                                    }}
                                                >
                                                    <canvas
                                                        ref={previewCanvasRef}
                                                        style={{
                                                            objectFit:
                                                                "contain",
                                                            width: 40,
                                                            height: 40,
                                                        }}
                                                    />
                                                </Card>
                                                <H5
                                                    style={{
                                                        lineHeight: "40px",
                                                        marginLeft: 50,
                                                        marginBottom: 0,
                                                    }}
                                                >
                                                    {entity.name}
                                                </H5>
                                                <div
                                                    className="multiline-ellipsis"
                                                    style={{
                                                        height: 36,
                                                        marginTop: 10,
                                                    }}
                                                >
                                                    {entity.description}
                                                </div>
                                                {!_.isEmpty(extra) ? (
                                                    <Tag
                                                        style={{
                                                            marginTop: 10,
                                                            maxWidth: `calc(100% - ${
                                                                _.isEqual(
                                                                    containerStatus,
                                                                    "not exist"
                                                                )
                                                                    ? 0
                                                                    : 36
                                                            }px)`,
                                                        }}
                                                        minimal
                                                        intent={Intent.PRIMARY}
                                                    >
                                                        {extra}
                                                    </Tag>
                                                ) : null}
                                            </Card>
                                        </Card>
                                    </Collapse>
                                    <ReactCrop
                                        style={{ marginTop: 15 }}
                                        keepSelection
                                        crop={crop}
                                        onChange={(_, percentCrop) =>
                                            setCrop(percentCrop)
                                        }
                                        onComplete={(c) => setCompletedCrop(c)}
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
                    {_.isEqual(tab, "icon") ? <div></div> : null}
                </div>
            </DialogBody>
            <DialogFooter>
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
            </DialogFooter>
        </Dialog>
    );
}

import {
    Button,
    ButtonGroup,
    Card,
    Collapse,
    Colors,
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
    faIcons,
    faImage,
} from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useRef, useState } from "react";
import ReactCrop, {
    centerCrop,
    convertToPixelCrop,
    makeAspectCrop,
} from "react-image-crop";
import "react-image-crop/dist/ReactCrop.css";
import { useDebounceEffect } from "../hooks/useDebounceEffect";
import { faIcon } from "../icon";
import { canvasPreview } from "./canvasPreview";
export default function EntityIconEditor({ isOpen, setIsIconEditorOpen }) {
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
        aspect,
        cropSize = 90
    ) => {
        return centerCrop(
            makeAspectCrop(
                { unit: "%", width: cropSize },
                aspect,
                mediaWidth,
                mediaHeight
            ),
            mediaWidth,
            mediaHeight
        );
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
        setCrop(centerAspectCrop(width, height, 1));
    };
    const [showPreview, setShowPreview] = useState(false);
    return (
        <Dialog
            onClose={() => {
                setIsIconEditorOpen(false);
                setImgSrc("");
                setShowPreview(false);
            }}
            title="Entity Icon"
            isOpen={isOpen}
        >
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
                </Card>
                <div style={{ padding: 15 }}>
                    {_.isEqual(tab, "image") ? (
                        <div>
                            <FileInput
                                style={{ width: 200 }}
                                text="Choose file..."
                                onInputChange={onSelectFile}
                            />
                            {!!imgSrc && (
                                <>
                                    <div
                                        style={{
                                            marginTop: 15,
                                            marginBottom: 15,
                                        }}
                                    >
                                        <ButtonGroup>
                                            <Button
                                                icon={faIcon({
                                                    icon: faArrowsToCircle,
                                                })}
                                                text="Center"
                                                onClick={() => {
                                                    const centerCrop =
                                                        centerAspectCrop(
                                                            imgRef.current
                                                                .width,
                                                            imgRef.current
                                                                .height,
                                                            1,
                                                            crop.height
                                                        );
                                                    setCrop(centerCrop);
                                                    setCompletedCrop(
                                                        convertToPixelCrop(
                                                            centerCrop,
                                                            imgRef.current
                                                                .width,
                                                            imgRef.current
                                                                .height
                                                        )
                                                    );
                                                }}
                                            />
                                            <Button
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
                                        </ButtonGroup>
                                        <Collapse
                                            keepChildrenMounted
                                            isOpen={showPreview}
                                        >
                                            <Card
                                                style={{
                                                    marginTop: 15,
                                                    width: 400,
                                                    padding: 15,
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
                                                            position:
                                                                "absolute",
                                                            left: 20,
                                                            top: 20,
                                                            padding: 0,
                                                            height: 40,
                                                            width: 40,
                                                            display: "flex",
                                                            justifyContent:
                                                                "center",
                                                            alignItems:
                                                                "center",
                                                        }}
                                                    >
                                                        <canvas
                                                            ref={
                                                                previewCanvasRef
                                                            }
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
                                                        Lorem
                                                    </H5>
                                                    <div
                                                        className="multiline-ellipsis"
                                                        style={{
                                                            height: 36,
                                                            marginTop: 10,
                                                        }}
                                                    >
                                                        Morbi mauris natoque
                                                        finibus parturient urna
                                                        at himenaeos.
                                                    </div>
                                                    <Tag
                                                        style={{
                                                            marginTop: 10,
                                                        }}
                                                        minimal
                                                        intent={Intent.PRIMARY}
                                                    >
                                                        consectetuer/adipiscing-elit
                                                    </Tag>
                                                </Card>
                                            </Card>
                                        </Collapse>
                                    </div>
                                    <ReactCrop
                                        keepSelection
                                        crop={crop}
                                        onChange={(_, percentCrop) =>
                                            setCrop(percentCrop)
                                        }
                                        onComplete={(c) => setCompletedCrop(c)}
                                        aspect={1}
                                        minWidth={40}
                                        minHeight={40}
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
                    text={`Apply ${tab}`}
                    large
                    icon={faIcon({ icon: faCheck })}
                />
            </DialogFooter>
        </Dialog>
    );
}

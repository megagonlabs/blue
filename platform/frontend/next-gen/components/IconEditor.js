import { canvasPreview } from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Classes,
    Colors,
    ControlGroup,
    FileInput,
    InputGroup,
    Intent,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { faSearch } from "@fortawesome/pro-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
    faCheck,
    faDotCircle,
    faFaceViewfinder,
    faIcons,
    faImage,
    faTelescope,
    faTrash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import ReactCrop, {
    centerCrop,
    convertToPixelCrop,
    makeAspectCrop,
} from "react-image-crop";
import "react-image-crop/dist/ReactCrop.css";
import { useShallow } from "zustand/react/shallow";
import { REGISTRY_ENTITY_ICON_WRAPPER_STYLES } from "./constants";
import { FAIcon } from "./FAIcon";
import { useDebounceEffect } from "./hooks/useDebounceEffect";
import NoResultsFound from "./nonidealstates/NoResultsFound";
import RegistryEntityIcon from "./registries/RegistryEntityIcon";
const COLOR_OPTIONS = [
    "#979B9D",
    "#FFA8A8",
    "#FAA2C1",
    "#E599F7",
    "#B197FC",
    "#91A7FF",
    "#74C0FC",
    "#66D9E8",
    "#50514F",
    "#FA5252",
    "#E64980",
    "#BE4BDB",
    "#7950F2",
    "#4C6EF5",
    "#228BE6",
    "#15AABF",
    "#111418",
    "#C92A2A",
    "#A61E4D",
    "#862E9C",
    "#5F3DC4",
    "#364FC7",
    "#1864AB",
    "#0B7285",
    "#63E6BE",
    "#8CE99A",
    "#C0EB75",
    "#FFE066",
    "#FFC078",
    "#F1B280",
    "#D3B79E",
    "#C2B9A0",
    "#12B886",
    "#40C057",
    "#82C91E",
    "#FAB005",
    "#FD7E14",
    "#D46E25",
    "#A87C56",
    "#867C65",
    "#087F5B",
    "#2B8A3E",
    "#5C940D",
    "#E67700",
    "#D9480F",
    "#8A4513",
    "#6F4B2D",
    "#4B4639",
];
function IconPicker({ content, setNewContent }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const { iconIndex, iconStore } = useAppStore(
        useShallow((state) => ({
            iconIndex: state.iconIndex,
            iconStore: state.iconStore,
        }))
    );
    const invalidColor = useRef(false);
    const [keyword, setKeyword] = useState("");
    const [colorHex, setColorHex] = useState(Colors.BLACK);
    const [iconName, setIconName] = useState(null);
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    useEffect(() => {
        setNewContent(`${iconName}:${colorHex}`);
    }, [colorHex, iconName]);
    useEffect(() => {
        setLoading(true);
        const isCanvas = _.isEqual(_.get(content, "type", null), "canvas");
        const [icon, color = Colors.BLACK] = _.split(content, ":");
        if (!isCanvas && !_.startsWith(content, "data:image/")) {
            setIconName(icon);
            setColorHex(color);
        }
        setLoading(false);
    }, [content]);
    const handleSearchQuery = useMemo(
        () =>
            _.debounce((keyword) => {
                if (!_.isEmpty(keyword)) {
                    const results = iconIndex.search(keyword);
                    setResults(results);
                } else {
                    setResults([]);
                }
            }, 800),
        [iconIndex]
    );
    useEffect(() => {
        handleSearchQuery(keyword);
    }, [keyword]);
    return (
        <div className="full-parent-dimension" style={{ display: "flex" }}>
            <div
                className="full-parent-height border-right"
                style={{
                    padding: 20,
                    overflowY: "auto",
                    width: "calc(100% - 320px)",
                }}
            >
                <InputGroup
                    className={loading ? Classes.SKELETON : null}
                    rightElement={
                        <Link
                            rel="noopener noreferrer"
                            target="_blank"
                            href="https://fontawesome.com/search?o=r&ic=pro-collection&s=solid&ip=sharp-duotone"
                        >
                            <Tooltip content="Advanced search">
                                <Button
                                    variant={ButtonVariant.MINIMAL}
                                    icon={<FAIcon icon={faTelescope} />}
                                    intent={Intent.PRIMARY}
                                />
                            </Tooltip>
                        </Link>
                    }
                    value={keyword}
                    onValueChange={(value) => {
                        setKeyword(value);
                    }}
                    autoFocus
                    size={Size.LARGE}
                    leftIcon={<FAIcon icon={faSearch} />}
                />
                <div
                    style={{
                        marginTop: 20,
                        display: "flex",
                        flexWrap: "wrap",
                        gap: 5,
                    }}
                >
                    {_.isEmpty(results) && <NoResultsFound />}
                    {results.map((id, index) => {
                        const name = _.get(iconStore, id, null);
                        return (
                            <div
                                key={index}
                                className="background-color-on-hover"
                                style={{
                                    ...REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
                                    cursor: "pointer",
                                    borderRadius: 2,
                                    backgroundColor: darkMode
                                        ? Colors.DARK_GRAY2
                                        : null,
                                }}
                                onClick={() => {
                                    setIconName(name);
                                }}
                            >
                                <FontAwesomeIcon
                                    color={colorHex}
                                    style={{ height: 20, width: 20 }}
                                    icon={["fasds", name]}
                                />
                            </div>
                        );
                    })}
                </div>
            </div>
            <div style={{ padding: 20, overflowY: "auto", width: 320 }}>
                <div
                    className={classNames(
                        "padding-0",
                        "overflow-hidden",
                        "custom-card",
                        { [Classes.SKELETON]: loading }
                    )}
                    style={{
                        ...REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
                        marginBottom: 20,
                    }}
                >
                    <RegistryEntityIcon content={`${iconName}:${colorHex}`} />
                </div>
                <ControlGroup style={{ marginBottom: 20 }}>
                    <Tag
                        className={loading ? Classes.SKELETON : null}
                        style={{
                            width: 30,
                            height: 30,
                            marginRight: 10,
                            marginTop: 5,
                            backgroundColor: _.isEmpty(colorHex)
                                ? Colors.BLACK
                                : colorHex,
                        }}
                    />
                    <InputGroup
                        className={loading ? Classes.SKELETON : null}
                        intent={invalidColor.current ? Intent.DANGER : null}
                        size={Size.LARGE}
                        value={colorHex}
                        onValueChange={(value) => {
                            const hex = _.toUpper(value);
                            setColorHex(hex);
                            if (/^#[0-9A-F]{6}$/i.test(hex)) {
                                invalidColor.current = false;
                            } else {
                                invalidColor.current = true;
                            }
                        }}
                    />
                </ControlGroup>
                <div
                    style={{
                        display: "grid",
                        gap: 5,
                        gridTemplateColumns:
                            "30px 30px 30px 30px 30px 30px 30px 30px",
                    }}
                >
                    {COLOR_OPTIONS.map((code, index) => {
                        const isWhite = _.isEqual(code, "#FFFFFF");
                        return (
                            <div
                                key={index}
                                onClick={() => {
                                    if (!isWhite) {
                                        invalidColor.current = false;
                                        setColorHex(
                                            _.isEqual(colorHex, code)
                                                ? Colors.BLACK
                                                : code
                                        );
                                    }
                                }}
                                style={{
                                    borderRadius: 2,
                                    width: 30,
                                    cursor: !isWhite && "pointer",
                                    height: 30,
                                    backgroundColor: !isWhite && code,
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "space-evenly",
                                }}
                            >
                                {_.isEqual(colorHex, code) ? (
                                    <FAIcon
                                        style={{ color: Colors.WHITE }}
                                        icon={faDotCircle}
                                    />
                                ) : null}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
function ImagePicker({ content, setNewContent }) {
    const [fileName, setFileName] = useState("Choose file...");
    const [crop, setCrop] = useState(null);
    const [completedCrop, setCompletedCrop] = useState(null);
    const [imgSrc, setImgSrc] = useState(content);
    const onSelectFile = (event) => {
        if (event.target.files && event.target.files.length > 0) {
            setCrop(null); // makes crop preview update between images.
            const reader = new FileReader();
            reader.addEventListener("load", () => {
                setImgSrc(reader.result?.toString() || "");
            });
            setFileName(event.target.files[0].name);
            reader.readAsDataURL(event.target.files[0]);
        }
    };
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
            fileReader.onload = () => resolve(fileReader.result);
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
    const onImageLoad = (event) => {
        const { width, height } = event.currentTarget;
        setCrop(centerAspectCrop(width, height));
    };
    const isImage = _.startsWith(imgSrc, "data:image/");
    useDebounceEffect(
        async () => {
            if (_.isNull(completedCrop)) return;
            if (
                completedCrop?.width &&
                completedCrop?.height &&
                imgRef.current &&
                previewCanvasRef.current
            ) {
                // we use canvasPreview as it's much faster than imgPreview.
                canvasPreview(
                    imgRef.current,
                    previewCanvasRef.current,
                    completedCrop
                );
            }
            const image = imgRef.current;
            const previewCanvas = previewCanvasRef.current;
            if (!image || !previewCanvas || !completedCrop) {
                throw new Error("Crop canvas does not exist");
            }
            // this will size relative to the uploaded image
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
            // uou might want { type: "image/jpeg", quality: <0 to 1> } to
            // reduce image size
            const blob = await offscreen.convertToBlob({
                type: "image/jpeg",
                quality: 1,
            });
            const dataURL = await readFileAsDataURL(blob);
            setNewContent(dataURL);
        },
        100,
        [completedCrop]
    );
    return (
        <div
            className="full-parent-dimension"
            style={{ padding: 20, overflow: "auto" }}
        >
            <ControlGroup fill>
                <FileInput
                    size={Size.LARGE}
                    inputProps={{ accept: "image/*" }}
                    text={fileName}
                    onInputChange={onSelectFile}
                />
                {!!imgSrc && isImage && (
                    <ButtonGroup
                        fill
                        variant={ButtonVariant.MINIMAL}
                        style={{ maxWidth: 150 }}
                    >
                        <Button
                            text="Center crop"
                            icon={<FAIcon icon={faFaceViewfinder} />}
                            onClick={centerCropManually}
                        />
                    </ButtonGroup>
                )}
            </ControlGroup>
            {!!imgSrc && isImage && (
                <div style={{ display: "flex", marginTop: 20 }}>
                    <ReactCrop
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
                    <div style={{ minWidth: 80, padding: "0px 20px" }}>
                        <div
                            className={classNames(
                                "padding-0",
                                "overflow-hidden",
                                "custom-card"
                            )}
                            style={REGISTRY_ENTITY_ICON_WRAPPER_STYLES}
                        >
                            <canvas
                                ref={previewCanvasRef}
                                style={{
                                    objectFit: "contain",
                                    width: 40,
                                    height: 40,
                                }}
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
export default function IconEditor({ content, setIcon, setShowIconEditor }) {
    const [tab, setTab] = useState("icon");
    useEffect(() => {
        if (_.startsWith(content, "data:image/")) {
            setTab("image");
        }
    }, [content]);
    const [newContent, setNewContent] = useState(null);
    const handleSetIcon = (contentValue) => {
        setIcon(contentValue);
        setShowIconEditor(false);
    };
    return (
        <div className="full-parent-dimension">
            <div style={{ padding: 10 }} className="border-bottom">
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    <Tooltip content="Icon" placement="bottom-start">
                        <Button
                            onClick={() => {
                                setTab("icon");
                            }}
                            active={_.isEqual(tab, "icon")}
                            icon={<FAIcon icon={faIcons} />}
                        />
                    </Tooltip>
                    <Tooltip content="Image" placement="bottom">
                        <Button
                            onClick={() => {
                                setTab("image");
                            }}
                            active={_.isEqual(tab, "image")}
                            icon={<FAIcon icon={faImage} />}
                        />
                    </Tooltip>
                </ButtonGroup>
                <div style={{ position: "absolute", right: 10, top: 10 }}>
                    <Tooltip content="Revert to default">
                        <Button
                            size={Size.LARGE}
                            intent={Intent.DANGER}
                            variant={ButtonVariant.MINIMAL}
                            icon={<FAIcon icon={faTrash} />}
                            onClick={() => {
                                handleSetIcon(null);
                            }}
                        />
                    </Tooltip>
                    <Button
                        style={{ marginLeft: 10 }}
                        size={Size.LARGE}
                        intent={Intent.SUCCESS}
                        text="Update"
                        icon={<FAIcon icon={faCheck} />}
                        onClick={() => {
                            handleSetIcon(newContent);
                        }}
                    />
                </div>
            </div>
            <div style={{ height: "calc(100% - 61px)" }}>
                {_.isEqual(tab, "icon") && (
                    <IconPicker
                        content={content}
                        setNewContent={setNewContent}
                    />
                )}{" "}
                {_.isEqual(tab, "image") && (
                    <ImagePicker
                        content={content}
                        setNewContent={setNewContent}
                    />
                )}
            </div>
        </div>
    );
}

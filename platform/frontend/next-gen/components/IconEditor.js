import { useAppStore } from "@/stores/app-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Card,
    Classes,
    Colors,
    ControlGroup,
    InputGroup,
    Intent,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
    faCheck,
    faDotCircle,
    faIcons,
    faImage,
    faSearch,
    faTelescope,
    faTrash,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import { REGISTRY_ENTITY_ICON_WRAPPER_STYLES } from "./constants";
import { FAIcon } from "./FAIcon";
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
                            <Tooltip
                                placement="bottom-end"
                                content="Advanced search"
                            >
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
                <Card
                    style={{
                        marginBottom: 20,
                        position: "relative",
                        height: 80,
                    }}
                >
                    <div
                        className={classNames(
                            "padding-0",
                            "overflow-hidden",
                            "custom-card",
                            { [Classes.SKELETON]: loading }
                        )}
                        style={{
                            ...REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
                            position: "absolute",
                            left: 20,
                            top: 20,
                        }}
                    >
                        <RegistryEntityIcon
                            content={`${iconName}:${colorHex}`}
                        />
                    </div>
                </Card>
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
                        const isWhite = _.isEqual("#FFFFFF", code);
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
                                    textAlign: "center",
                                    lineHeight: "30px",
                                    backgroundColor: !isWhite && code,
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
                    <Tooltip content="Revert to default icon">
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
                )}
            </div>
        </div>
    );
}

import { COLOR_OPTIONS, ENTITY_ICON_40 } from "@/components/constant";
import {
    Button,
    Card,
    ControlGroup,
    InputGroup,
    Intent,
    Tag,
} from "@blueprintjs/core";
import {
    faArrowUpRightFromSquare,
    faDotCircle,
    faSearch,
    faTelescope,
} from "@fortawesome/pro-duotone-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import _ from "lodash";
import Link from "next/link";
import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { AppContext } from "../contexts/app-context";
import { faIcon } from "../icon";
import RegistryCard from "../registry/RegistryCard";
export default function IconPicker({
    icon,
    color,
    setIcon,
    setColor,
    entity,
    extra,
}) {
    const { appState } = useContext(AppContext);
    const [keyword, setKeyword] = useState("");
    const [searchResults, setSearchResults] = useState([]);
    const invalidColor = useRef(false);
    const [colorHex, setColorHex] = useState(color);
    useEffect(() => {
        setColorHex(_.isEmpty(color) ? "" : color);
        invalidColor.current = false;
    }, [color]);
    const handleSearchQuery = useCallback(
        _.debounce((keyword) => {
            if (!_.isEmpty(keyword)) {
                const results = appState.app.iconPickerIndex.search(keyword);
                setSearchResults(results);
            } else {
                setSearchResults([]);
            }
        }, 800),
        []
    );
    return (
        <>
            <InputGroup
                autoFocus
                leftIcon={faIcon({ icon: faSearch })}
                placeholder="Search icons"
                large
                value={keyword}
                onChange={(event) => {
                    setKeyword(event.target.value);
                    handleSearchQuery.call({}, event.target.value);
                }}
                style={{
                    marginBottom:
                        !_.isEmpty(searchResults) || !_.isEmpty(icon) ? 15 : 0,
                }}
                rightElement={
                    <Link
                        target="_blank"
                        href="https://fontawesome.com/search?o=r&s=solid&f=duotone"
                    >
                        <Button
                            icon={faIcon({ icon: faTelescope })}
                            intent={Intent.PRIMARY}
                            minimal
                            rightIcon={faIcon({
                                icon: faArrowUpRightFromSquare,
                            })}
                            text="Advanced"
                        />
                    </Link>
                }
            />
            {!_.isEmpty(searchResults) || !_.isEmpty(icon) ? (
                <div
                    style={{
                        position: "relative",
                        display: "flex",
                        gap: 15,
                        paddingBottom: 15,
                    }}
                >
                    <Card
                        style={{
                            boxShadow: "none",
                            padding: 7.5,
                            display: "grid",
                            width: 155,
                            gap: 10,
                            gridAutoRows: 40,
                            gridTemplateColumns: "40px 40px 40px",
                        }}
                    >
                        {searchResults.map((id, index) => {
                            const iconName = _.get(
                                appState,
                                ["app", "iconPickerStore", id],
                                null
                            );
                            return (
                                <div
                                    className="on-hover-background-color-bp-gray-3"
                                    key={index}
                                    style={{
                                        ...ENTITY_ICON_40,
                                        borderRadius: 2,
                                        cursor: "pointer",
                                    }}
                                    onClick={() => {
                                        setIcon(iconName);
                                    }}
                                >
                                    <FontAwesomeIcon
                                        style={{ height: 20, width: 20 }}
                                        icon={["fad", iconName]}
                                    />
                                </div>
                            );
                        })}
                    </Card>
                    <div
                        style={{
                            position: "sticky",
                            top: 120,
                            width: "calc(100% - 170px)",
                            alignSelf: "flex-start",
                        }}
                    >
                        <Card
                            style={{
                                padding: 20,
                                boxShadow: "none",
                                width: 350,
                            }}
                        >
                            <RegistryCard
                                type={entity.type}
                                title={entity.name}
                                description={entity.description}
                                extra={extra}
                                container={entity.container}
                                previewIcon={
                                    !_.isEmpty(icon) ? (
                                        <FontAwesomeIcon
                                            color={color}
                                            style={{ height: 20, width: 20 }}
                                            icon={["fad", icon]}
                                        />
                                    ) : null
                                }
                            />
                        </Card>
                        <Card
                            style={{
                                boxShadow: "none",
                                marginTop: 15,
                            }}
                        >
                            <ControlGroup style={{ marginBottom: 10 }}>
                                <Tag
                                    style={{
                                        backgroundColor: _.isEmpty(color)
                                            ? "#1C2127"
                                            : color,
                                        height: 30,
                                        width: 30,
                                        marginTop: 5,
                                        marginRight: 5,
                                    }}
                                />
                                <InputGroup
                                    intent={
                                        invalidColor.current
                                            ? Intent.DANGER
                                            : null
                                    }
                                    large
                                    onChange={(event) => {
                                        const value = _.toUpper(
                                            event.target.value
                                        );
                                        setColorHex(value);
                                        if (/^#[0-9A-F]{6}$/i.test(value)) {
                                            setColor(value);
                                            invalidColor.current = false;
                                        } else {
                                            invalidColor.current = true;
                                        }
                                    }}
                                    value={colorHex}
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
                                                    setColor(
                                                        _.isEqual(color, code)
                                                            ? "#1C2127"
                                                            : code
                                                    );
                                                }
                                            }}
                                            style={{
                                                borderRadius: 2,
                                                cursor: !isWhite && "pointer",
                                                userSelect: "none",
                                                width: 30,
                                                height: 30,
                                                backgroundColor:
                                                    !isWhite && code,
                                                textAlign: "center",
                                                lineHeight: "30px",
                                            }}
                                        >
                                            {_.isEqual(color, code)
                                                ? faIcon({
                                                      icon: faDotCircle,
                                                      style: { color: "white" },
                                                  })
                                                : null}
                                        </div>
                                    );
                                })}
                            </div>
                        </Card>
                    </div>
                </div>
            ) : null}
        </>
    );
}

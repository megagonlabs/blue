import { COLOR_OPTIONS, ENTITY_ICON_40 } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import RegistryCard from "@/components/registry/RegistryCard";
import {
    Button,
    Card,
    ControlGroup,
    InputGroup,
    Intent,
    Tag,
} from "@blueprintjs/core";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
    faArrowUpRightFromSquare,
    faDotCircle,
    faSearch,
    faTelescope,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import Link from "next/link";
import { useContext, useEffect, useMemo, useRef, useState } from "react";
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
    const handleSearchQuery = useMemo(
        () =>
            _.debounce((keyword) => {
                if (!_.isEmpty(keyword)) {
                    const results =
                        appState.app.iconPickerIndex.search(keyword);
                    setSearchResults(results);
                } else {
                    setSearchResults([]);
                }
            }, 800),
        [appState.app.iconPickerIndex]
    );
    return (
        <>
            <InputGroup
                autoFocus
                leftIcon={faIcon({ icon: faSearch })}
                placeholder="Search icons"
                size="large"
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
                        rel="noopener noreferrer"
                        target="_blank"
                        href="https://fontawesome.com/search?o=r&s=solid&f=sharp-duotone"
                    >
                        <Button
                            icon={faIcon({ icon: faTelescope })}
                            intent={Intent.PRIMARY}
                            variant="minimal"
                            endIcon={faIcon({
                                icon: faArrowUpRightFromSquare,
                            })}
                            text="Advanced"
                        />
                    </Link>
                }
            />
            {!_.isEmpty(searchResults) || !_.isEmpty(icon) ? (
                <div style={{ position: "relative", display: "flex", gap: 15 }}>
                    <Card
                        style={{
                            boxShadow: "none",
                            padding: 7.5,
                            display: "grid",
                            width: 155,
                            maxHeight: 476,
                            overflowY: "auto",
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
                                    className="background-color-on-hover"
                                    key={index}
                                    style={{
                                        ...ENTITY_ICON_40,
                                        borderRadius: 2,
                                        cursor: "pointer",
                                    }}
                                    onClick={() => setIcon(iconName)}
                                >
                                    <FontAwesomeIcon
                                        style={{ height: 20, width: 20 }}
                                        icon={["fasds", iconName]}
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
                                icon={[icon, color]}
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
                                    size="large"
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

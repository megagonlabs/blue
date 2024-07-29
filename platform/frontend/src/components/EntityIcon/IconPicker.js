import { COLOR_OPTIONS, ENTITY_ICON_40 } from "@/components/constant";
import { Card, InputGroup } from "@blueprintjs/core";
import { faDotCircle, faSearch } from "@fortawesome/pro-duotone-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import _ from "lodash";
import { useCallback, useContext, useState } from "react";
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
                style={{ marginBottom: 15 }}
            />
            <div style={{ position: "relative", display: "flex", gap: 15 }}>
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
                            ["app", "iconPickerStore", id, "iconName"],
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
                    <Card style={{ padding: 20, boxShadow: "none" }}>
                        <RegistryCard
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
                            padding: 20,
                            boxShadow: "none",
                            display: "grid",
                            marginTop: 15,
                            gap: 5,
                            gridTemplateColumns:
                                "30px 30px 30px 30px 30px 30px",
                        }}
                    >
                        {COLOR_OPTIONS.map((code, index) => {
                            const isWhite = _.isEqual("#FFFFFF", code);
                            return (
                                <div
                                    key={index}
                                    onClick={() => {
                                        if (!isWhite) {
                                            setColor(code);
                                        }
                                    }}
                                    style={{
                                        borderRadius: 2,
                                        cursor: !isWhite && "pointer",
                                        userSelect: "none",
                                        width: 30,
                                        height: 30,
                                        backgroundColor: !isWhite && code,
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
                    </Card>
                </div>
            </div>
        </>
    );
}

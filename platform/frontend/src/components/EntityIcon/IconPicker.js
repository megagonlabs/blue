import { COLOR_OPTIONS, ENTITY_ICON_40 } from "@/components/constant";
import { Card, InputGroup } from "@blueprintjs/core";
import { faSearch } from "@fortawesome/pro-duotone-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import _ from "lodash";
import { useCallback, useContext, useState } from "react";
import { AppContext } from "../contexts/app-context";
import { faIcon } from "../icon";
export default function IconPicker({ icon, color, setIcon, setColor }) {
    const { appState } = useContext(AppContext);
    const [keyword, setKeyword] = useState("");
    const [loading, setLoading] = useState(true);
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
                style={{ marginBottom: !_.isEmpty(searchResults) ? 15 : 0 }}
            />
            {!_.isEmpty(searchResults) ? (
                <div style={{ position: "relative", display: "flex", gap: 15 }}>
                    <Card
                        style={{
                            boxShadow: "none",
                            padding: 7.5,
                            display: "grid",
                            width: 205,
                            gap: 10,
                            gridAutoRows: 40,
                            gridTemplateColumns: "40px 40px 40px 40px",
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
                                        fontSize={20}
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
                            width: "calc(100% - 205px)",
                            alignSelf: "flex-start",
                        }}
                    >
                        <Card style={{ padding: 10, boxShadow: "none" }}>
                            {!_.isEmpty(icon) ? (
                                <FontAwesomeIcon
                                    color={color}
                                    fontSize={40}
                                    icon={["fad", icon]}
                                />
                            ) : null}
                        </Card>
                        <div
                            style={{
                                display: "grid",
                                marginTop: 15,
                                gap: 5,
                                gridTemplateColumns:
                                    "20px 20px 20px 20px 20px 20px",
                            }}
                        >
                            {COLOR_OPTIONS.map((color, index) => (
                                <div
                                    key={index}
                                    onClick={() => {
                                        setColor(color);
                                    }}
                                    style={{
                                        cursor: "pointer",
                                        width: 20,
                                        height: 20,
                                        backgroundColor: color,
                                        visibility: _.isEqual("#FFFFFF", color)
                                            ? "hidden"
                                            : null,
                                    }}
                                >
                                    &nbsp;
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            ) : null}
        </>
    );
}

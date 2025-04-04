import { ENTITY_TYPE_LOOKUP } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { Card, Classes } from "@blueprintjs/core";
import _ from "lodash";
import Link from "next/link";
import { useContext } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList } from "react-window";
export default function SearchList({ type }) {
    const { appState } = useContext(AppContext);
    return (
        <AutoSizer>
            {({ width, height }) => (
                <FixedSizeList
                    style={{ paddingBottom: 10 }}
                    height={height}
                    width={width}
                    itemCount={appState[type].list.length}
                    itemSize={69}
                >
                    {({ index, style }) => {
                        const item = appState[type].list[index];
                        const registryName = appState[type].registryName;
                        let link = "",
                            path = [];
                        link = `/registry/${registryName}`;
                        path = [type];
                        if (_.isEqual(type, "data")) {
                            path = [type, "database", "collection"];
                        }
                        const scopes = item.scope.split("/");
                        for (var i = 0; i < scopes.length; i++) {
                            if (_.isEmpty(scopes[i])) continue;
                            link += `/${path.shift()}`;
                            link += `/${scopes[i]}`;
                        }
                        let itemType = item.type;
                        if (_.isEqual(itemType, "source")) {
                            itemType = "data";
                        }
                        link += `/${itemType}/${item.name}`;
                        return (
                            <div style={style}>
                                <Link
                                    href={link}
                                    className="no-link-decoration"
                                    style={{ color: "initial" }}
                                >
                                    <Card
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "space-between",
                                            padding: "18px 20px",
                                            margin: "1px 21px 10px 21px",
                                        }}
                                    >
                                        <div
                                            style={{
                                                display: "flex",
                                                alignItems: "center",
                                            }}
                                        >
                                            <div
                                                className={Classes.TEXT_MUTED}
                                                style={{ marginRight: 20 }}
                                            >
                                                {faIcon({
                                                    icon: ENTITY_TYPE_LOOKUP[
                                                        item.type
                                                    ].icon,
                                                    size: 21,
                                                })}
                                            </div>
                                            <div
                                                className={Classes.TEXT_MUTED}
                                                style={{ marginRight: 10 }}
                                            >
                                                {item.scope}
                                                {item.scope.length > 1 && "/"}
                                                {item.type}
                                            </div>
                                            <div>{item.name}</div>
                                        </div>
                                        {!_.isNil(item.score) ? (
                                            <div
                                                className={
                                                    Classes.TEXT_DISABLED
                                                }
                                            >
                                                {item.score}
                                            </div>
                                        ) : null}
                                    </Card>
                                </Link>
                            </div>
                        );
                    }}
                </FixedSizeList>
            )}
        </AutoSizer>
    );
}

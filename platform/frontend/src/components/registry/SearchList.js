import { Card, Classes } from "@blueprintjs/core";
import _ from "lodash";
import Link from "next/link";
import { useContext } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList } from "react-window";
import { AppContext } from "../app-context";
import { SEARCH_LIST_TYPE_LOOKUP } from "../constant";
import { faIcon } from "../icon";
export default function SearchList({ type }) {
    const { appState } = useContext(AppContext);
    return (
        <AutoSizer>
            {({ width, height }) => (
                <FixedSizeList
                    style={{ padding: "0px 21px 10px 21px" }}
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
                        if (_.isEqual(type, "agent")) {
                            link = `/agents/${registryName}`;
                            path = ["agent"];
                        } else if (_.isEqual(type, "data")) {
                            link = `/data/${registryName}`;
                            path = ["source", "database"];
                        }
                        const scopes = item.scope.split("/");
                        for (var i = 0; i < scopes.length; i++) {
                            if (_.isEmpty(scopes[i])) continue;
                            link += `/${path.shift()}`;
                            link += `/${scopes[i]}`;
                        }
                        link += `/${item.type}/${item.name}`;
                        return (
                            <div style={style}>
                                <Link href={link}>
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
                                                style={{ marginRight: 10 }}
                                            >
                                                {faIcon({
                                                    icon: SEARCH_LIST_TYPE_LOOKUP[
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

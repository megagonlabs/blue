import { Card, Classes } from "@blueprintjs/core";
import _ from "lodash";
import Link from "next/link";
import { useContext } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList } from "react-window";
import { AppContext } from "../app-context";
export default function SearchList({ type }) {
    const { appState } = useContext(AppContext);
    return (
        <AutoSizer>
            {({ width, height }) => (
                <FixedSizeList
                    style={{ padding: "0px 21px 20px 21px" }}
                    height={height}
                    width={width}
                    itemCount={appState[type].list.length}
                    itemSize={68}
                >
                    {({ index, style }) => {
                        const item = appState[type].list[index];
                        let link = "";
                        if (_.isEqual(type, "agent")) {
                            link = `/agents/${appState[type].registryName}`;
                            if (item.scope.length > 1) {
                                link += `/agent/${item.scope}`;
                            }
                            link += `/${item.type}/${item.name}`;
                        }
                        return (
                            <div style={style}>
                                <Card
                                    style={{
                                        margin: "10px 21px 0px 21px",
                                        padding: "0px 20px",
                                        lineHeight: "58px",
                                    }}
                                >
                                    <Link
                                        style={{ display: "flex" }}
                                        href={link}
                                    >
                                        <div
                                            className={Classes.TEXT_MUTED}
                                            style={{ marginRight: 10 }}
                                        >
                                            <span>
                                                {item.scope}
                                                {item.scope.length > 1 && "/"}
                                                {item.type}
                                            </span>
                                        </div>
                                        <div>{item.name}</div>
                                    </Link>
                                </Card>
                            </div>
                        );
                    }}
                </FixedSizeList>
            )}
        </AutoSizer>
    );
}

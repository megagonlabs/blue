import { Card } from "@blueprintjs/core";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList } from "react-window";
export default function SessionList() {
    return (
        <Card style={{ height: "100%", padding: 15, borderRadius: 0 }}>
            <AutoSizer>
                {({ width, height }) => (
                    <FixedSizeList height={height} width={width}>
                        {/* {Row} */}
                    </FixedSizeList>
                )}
            </AutoSizer>
        </Card>
    );
}

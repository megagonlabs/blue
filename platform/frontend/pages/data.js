import DataSourceList from "@/components/data/DataSourceList";
import { H4 } from "@blueprintjs/core";
export default function Data() {
    return (
        <>
            <div
                style={{
                    // position: "absolute",
                    top: 20,
                    left: 20,
                    height: "100%",
                    width: "100%",
                }}
            >
                <H4
                    className="margin-0"
                    style={{
                        lineHeight: "30px",
                        marginRight: 10,
                    }}
                >
                    Data Registry (default)
                </H4>
                <DataSourceList />
            </div>
        </>
    );
}

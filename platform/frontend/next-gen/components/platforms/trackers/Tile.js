import Timestamp from "@/components/Timestamp";
import { useAppStore } from "@/stores/app-store";
import { Card, Classes, Colors } from "@blueprintjs/core";
export default function Tile({ type, label, object }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const { value } = object;
    return (
        <Card
            style={{
                padding: darkMode ? 1 : 0,
                overflow: "hidden",
            }}
        >
            <div
                style={{ padding: "10px 10px 5px" }}
                className={Classes.TEXT_MUTED}
            >
                {label}
            </div>
            <div
                style={{
                    height: "50%",
                    padding: "5px 10px 10px",
                    backgroundColor: darkMode
                        ? Colors.DARK_GRAY3
                        : Colors.LIGHT_GRAY5,
                }}
            >
                {_.isEqual(type, "time") ? (
                    <Timestamp date={value * 1000} />
                ) : (
                    value
                )}
            </div>
        </Card>
    );
}

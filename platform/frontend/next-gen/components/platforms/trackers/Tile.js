import Timestamp from "@/components/Timestamp";
import { useAppStore } from "@/stores/app-store";
import { Classes, Colors } from "@blueprintjs/core";
import _ from "lodash";
export default function Tile({ type, label, object }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const { value } = object;
    return (
        <div className="custom-card" style={{ overflow: "hidden" }}>
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
                        : Colors.LIGHT_GRAY4,
                }}
            >
                {_.isEqual(type, "time") ? (
                    <Timestamp epoch={value * 1000} />
                ) : (
                    value
                )}
            </div>
        </div>
    );
}

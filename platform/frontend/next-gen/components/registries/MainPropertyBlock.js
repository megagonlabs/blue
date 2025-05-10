import { MAIN_INFO_STYLES } from "@/components/constants";
import { Classes } from "@blueprintjs/core";
import classNames from "classnames";
export default function MainPropertyBlock({ loading, label, children }) {
    return (
        <div style={MAIN_INFO_STYLES}>
            <div
                className={classNames(
                    Classes.TEXT_MUTED,
                    Classes.TEXT_OVERFLOW_ELLIPSIS
                )}
            >
                {label}
            </div>
            <div
                className={loading ? Classes.SKELETON : null}
                style={{ fontWeight: 600 }}
            >
                {children}
            </div>
        </div>
    );
}

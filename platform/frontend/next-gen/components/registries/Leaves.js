import { useAppStore } from "@/stores/app-store";
import { Classes, Colors } from "@blueprintjs/core";
import classNames from "classnames";
import _ from "lodash";
import EntityDisplayName from "./EntityDisplayName";
export default function Leaves({ list, addCrumb, loading }) {
    const darkMode = useAppStore((state) => state.darkMode);
    return (
        <div
            className={classNames("full-parent-width", {
                [Classes.SKELETON]: loading,
                "responsive-grid-container": !loading,
            })}
        >
            {_.isEmpty(list) && "-"}
            {list.map((element, index) => {
                return (
                    <div
                        onClick={() => {
                            addCrumb(element);
                        }}
                        className="grid-item"
                        key={index}
                        style={{
                            cursor: "pointer",
                            padding: 15,
                            backgroundColor: darkMode
                                ? Colors.DARK_GRAY1
                                : Colors.LIGHT_GRAY5,
                        }}
                    >
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{
                                fontWeight: 600,
                                color: darkMode ? Colors.BLUE5 : Colors.BLUE2,
                            }}
                        >
                            <EntityDisplayName entity={element} />
                        </div>
                        <div
                            className={classNames(
                                Classes.TEXT_MUTED,
                                Classes.TEXT_OVERFLOW_ELLIPSIS
                            )}
                        >
                            {element.description}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

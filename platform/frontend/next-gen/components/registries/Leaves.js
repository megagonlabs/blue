import { useAppStore } from "@/stores/app-store";
import { Classes, Colors } from "@blueprintjs/core";
import classNames from "classnames";
import _ from "lodash";
import EntityDisplayName from "./EntityDisplayName";
export default function Leaves({ list, addCrumb, loading, isEditing }) {
    const darkMode = useAppStore((state) => state.dark_mode);
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
                        className={classNames("grid-item", {
                            "pointer-events-none": isEditing,
                        })}
                        key={index}
                        style={{
                            cursor: "pointer",
                            padding: 20,
                            backgroundColor: darkMode
                                ? Colors.DARK_GRAY1
                                : Colors.LIGHT_GRAY5,
                            borderRadius: 2,
                        }}
                    >
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{
                                fontWeight: 600,
                                color: isEditing
                                    ? null
                                    : darkMode
                                    ? Colors.BLUE5
                                    : Colors.BLUE2,
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

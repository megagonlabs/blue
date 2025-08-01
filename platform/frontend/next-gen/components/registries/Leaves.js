import { useAppStore } from "@/stores/app-store";
import { Classes, Colors } from "@blueprintjs/core";
import classNames from "classnames";
import _ from "lodash";
import { REGISTRY_ENTITY_ICON_WRAPPER_STYLES } from "../constants";
import EntityDisplayName from "./EntityDisplayName";
import RegistryEntityIcon from "./RegistryEntityIcon";
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
                            position: "relative",
                        }}
                    >
                        <div
                            className={classNames(
                                "padding-0",
                                "overflow-hidden",
                                "custom-card",
                                { [Classes.SKELETON]: loading }
                            )}
                            style={{
                                ...REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
                                position: "absolute",
                                left: 20,
                                top: 20,
                            }}
                        >
                            <RegistryEntityIcon
                                type={element.type}
                                content={_.get(element, "icon", null)}
                            />
                        </div>
                        <div
                            style={{
                                marginLeft: 60,
                                display: "flex",
                                flexDirection: "column",
                                height: 40,
                                justifyContent: "space-between",
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
                    </div>
                );
            })}
        </div>
    );
}

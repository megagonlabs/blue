import { HEX_TRANSPARENCY } from "@/components/constants";
import { JSONFORMS_RENDERERS } from "@/components/jsonforms/renderers";
import { useAppStore } from "@/stores/app-store";
import { useSessionStore } from "@/stores/session-store";
import { Colors, Size, Tag } from "@blueprintjs/core";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells } from "@jsonforms/vanilla-renderers";
import _ from "lodash";
import { useEffect } from "react";
import { useErrorBoundary } from "react-use-error-boundary";
import { useShallow } from "zustand/react/shallow";
export default function JSONForm({ content, hasError }) {
    const { forms, setFormData } = useSessionStore(
        useShallow((state) => ({
            forms: state.forms,
            setFormData: state.setFormData,
        }))
    );
    const darkMode = useAppStore((state) => state.dark_mode);
    const id = _.get(content, "form_id", null);
    const specifications = _.get(forms, [id, "content"], {});
    const closed = _.get(forms, [id, "closed"], {});
    const [error] = useErrorBoundary();
    useEffect(() => {
        if (hasError) {
            hasError.current = Boolean(error);
        }
    }, [error, hasError]);
    return !error ? (
        <>
            <JsonForms
                schema={_.get(specifications, "schema", {})}
                data={_.get(specifications, "data", {})}
                uischema={_.get(specifications, "uischema", {})}
                renderers={JSONFORMS_RENDERERS}
                cells={vanillaCells}
                onChange={({ data, errors }) => {
                    console.log(data, errors);
                    setFormData(id, data);
                }}
            />
            {closed && (
                <>
                    <Tag
                        fill
                        size={Size.LARGE}
                        style={{
                            position: "absolute",
                            left: 0,
                            bottom: 0,
                            zIndex: 1,
                            borderTopLeftRadius: 0,
                            borderTopRightRadius: 0,
                        }}
                    >
                        Closed
                    </Tag>
                    <div
                        style={{
                            position: "absolute",
                            top: 0,
                            left: 0,
                            backgroundColor: `${
                                darkMode
                                    ? Colors.DARK_GRAY5
                                    : Colors.LIGHT_GRAY1
                            }${HEX_TRANSPARENCY[50]}`,
                        }}
                        className="full-parent-dimension"
                    >
                        &nbsp;
                    </div>
                </>
            )}
        </>
    ) : (
        String(error)
    );
}

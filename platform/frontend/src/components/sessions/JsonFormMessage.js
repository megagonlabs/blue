import { HEX_TRANSPARENCY, JSONFORMS_RENDERERS } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { Colors, Tag } from "@blueprintjs/core";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells } from "@jsonforms/vanilla-renderers";
import classNames from "classnames";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { useErrorBoundary } from "react-use-error-boundary";
export default function JsonFormMessage({ content, hasError }) {
    const { appState } = useContext(AppContext);
    const terminatedInteraction = appState.session.terminatedInteraction;
    const [error] = useErrorBoundary();
    const [data, setData] = useState(_.get(content, "data", {}));
    const isFormTerminated = terminatedInteraction.has(
        _.get(content, "form_id", null)
    );
    useEffect(() => {
        hasError.current = Boolean(error);
    }, [error]);
    return !error ? (
        <>
            <JsonForms
                schema={_.get(content, "schema", {})}
                data={data}
                uischema={_.get(content, "uischema", {})}
                renderers={JSONFORMS_RENDERERS}
                cells={vanillaCells}
                onChange={({ data, errors }) => {
                    console.log(data, errors);
                    setData(data);
                }}
            />
            {isFormTerminated ? (
                <>
                    <Tag
                        fill
                        large
                        style={{
                            position: "absolute",
                            left: 0,
                            bottom: 0,
                            borderTopLeftRadius: 0,
                            borderTopRightRadius: 0,
                            zIndex: 21,
                        }}
                    >
                        Closed
                    </Tag>
                    <div
                        style={{
                            position: "absolute",
                            top: 0,
                            left: 0,
                            backgroundColor: `${Colors.LIGHT_GRAY3}${HEX_TRANSPARENCY[50]}`,
                        }}
                        className={classNames(
                            "full-parent-width",
                            "full-parent-height"
                        )}
                    >
                        &nbsp;
                    </div>
                </>
            ) : null}
        </>
    ) : (
        String(error)
    );
}

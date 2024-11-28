import { HEX_TRANSPARENCY, JSONFORMS_RENDERERS } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { Colors, Tag } from "@blueprintjs/core";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells } from "@jsonforms/vanilla-renderers";
import classNames from "classnames";
import _ from "lodash";
import { useContext, useEffect } from "react";
import { useErrorBoundary } from "react-use-error-boundary";
export default function JsonForm({ content, hasError }) {
    const { appState, appActions } = useContext(AppContext);
    const { closedJsonforms, jsonformSpecs } = appState.session;
    const [error] = useErrorBoundary();
    const formId = _.get(content, "form_id", null);
    const formSpec = _.get(jsonformSpecs, formId, {});
    const isFormClosed = closedJsonforms.has(formId);
    useEffect(() => {
        hasError.current = Boolean(error);
    }, [error]); // eslint-disable-line react-hooks/exhaustive-deps
    return !error ? (
        <>
            <JsonForms
                schema={_.get(formSpec, "schema", {})}
                data={_.get(formSpec, "data", {})}
                uischema={_.get(formSpec, "uischema", {})}
                renderers={JSONFORMS_RENDERERS}
                cells={vanillaCells}
                onChange={({ data, errors }) => {
                    console.log(data, errors);
                    appActions.session.setFormData({ data, formId });
                }}
            />
            {isFormClosed || 1 ? (
                <>
                    <Tag
                        fill
                        large
                        style={{
                            position: "absolute",
                            left: 0,
                            backgroundColor: Colors.GRAY2,
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
                            zIndex: 5,
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

import { JSONFORMS_RENDERERS } from "@/components/constant";
import { Callout } from "@blueprintjs/core";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells } from "@jsonforms/vanilla-renderers";
import _ from "lodash";
import { useEffect, useState } from "react";
import { useErrorBoundary } from "react-use-error-boundary";
export default function InteractiveMessage({ type, content, setHasError }) {
    if (_.isEqual(type, "INTERACTIVE_CALLOUT")) {
        return (
            <Callout icon={null} intent={_.get(content, "intent", null)}>
                {_.get(content, "message", "")}
            </Callout>
        );
    }
    const [error] = useErrorBoundary();
    const [data, setData] = useState(_.get(content, "data", {}));
    useEffect(() => {
        setHasError(Boolean(error));
    }, [error]);
    return !error ? (
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
    ) : (
        String(error)
    );
}

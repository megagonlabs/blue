import { JSONFORMS_RENDERERS } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { Callout, Intent, Tag } from "@blueprintjs/core";
import { faCheck } from "@fortawesome/pro-duotone-svg-icons";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells } from "@jsonforms/vanilla-renderers";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { useErrorBoundary } from "react-use-error-boundary";
export default function InteractiveMessage({ stream, content, setHasError }) {
    const { appState } = useContext(AppContext);
    const terminatedInteraction = appState.session.terminatedInteraction;
    const contentType = _.get(content, "type", null);
    const contentValue = _.get(content, "content", {});
    const [error] = useErrorBoundary();
    const [data, setData] = useState(_.get(contentValue, "data", {}));
    useEffect(() => {
        setHasError(Boolean(error));
    }, [error]);
    if (
        terminatedInteraction.has(`${stream},${_.get(content, "form_id", "")}`)
    ) {
        return (
            <Tag
                minimal
                large
                intent={Intent.SUCCESS}
                icon={faIcon({ icon: faCheck })}
            >
                Interactions complete.
            </Tag>
        );
    } else if (_.isEqual(contentType, "CALLOUT")) {
        return (
            <Callout
                icon={null}
                intent={_.get(content, "content.intent", null)}
            >
                {_.get(content, "content.message", "")}
            </Callout>
        );
    }
    // contentType == "UI"
    return !error ? (
        <JsonForms
            schema={_.get(contentValue, "schema", {})}
            data={data}
            uischema={_.get(contentValue, "uischema", {})}
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

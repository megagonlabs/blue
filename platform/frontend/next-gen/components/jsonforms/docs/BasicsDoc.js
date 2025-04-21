import JsonViewer from "@/components/JsonViewer";
import { Callout, Code, H1, H2, H3, Intent, Pre } from "@blueprintjs/core";
export default function BasicsDoc() {
    return (
        <div>
            <H1 style={{ marginTop: 0 }}>Basics</H1>
            <Callout intent={Intent.PRIMARY} icon={null}>
                For full documentation on JSONForms, please visit&nbsp;
                <a
                    rel="noopener noreferrer"
                    target="_blank"
                    href="https://jsonforms.io/"
                >
                    here
                </a>
                .
            </Callout>
            <H2>Controls</H2>
            <div>
                Controls represent the basic building blocks for creating forms.
            </div>
            <div>
                A control is usually displaying the value of one property from
                the data in an UI element such as an input field.
            </div>
            <div>
                How a control is rendered depends on the type of the property as
                defined in the JSON Schema, e.g. a property of type boolean is
                rendered as a Checkbox by default.
            </div>
            <H3>scope &#40;string&#41;</H3>
            <div>
                The mandatory <Code>scope</Code> property, which expects a&nbsp;
                <a
                    rel="noopener noreferrer"
                    target="_blank"
                    href="https://json-schema.org/understanding-json-schema/structuring"
                >
                    JSON schema reference value
                </a>
                , defines to which property of the data the control should be
                bound to. For instance, let&apos;s suppose we want to create a
                control for the name property in this schema:
            </div>
            <Pre>
                <JsonViewer
                    enableClipboard={false}
                    json={{
                        properties: {
                            name: {
                                type: "string",
                            },
                        },
                    }}
                />
            </Pre>
            <div>
                The corresponding UI Schema needs to set the type of the UI
                Schema Element to <Code>Control</Code> and set the scope to
                point to the name property from the JSON schema as follows:
            </div>
            <Pre>
                <JsonViewer
                    enableClipboard={false}
                    json={{
                        type: "Control",
                        scope: "#/properties/name",
                    }}
                />
            </Pre>
        </div>
    );
}

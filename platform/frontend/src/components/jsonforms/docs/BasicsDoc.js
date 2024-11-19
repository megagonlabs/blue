import { faIcon } from "@/components/icon";
import JsonViewer from "@/components/sessions/message/renderers/JsonViewer";
import {
    Button,
    Callout,
    Classes,
    Code,
    H1,
    H2,
    H3,
    Intent,
    Pre,
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/sharp-duotone-solid-svg-icons";
export default function BasicsDoc({ closePanel }) {
    return (
        <>
            <div className="border-bottom" style={{ padding: "10px 20px" }}>
                <Button
                    outlined
                    text="Back"
                    onClick={closePanel}
                    icon={faIcon({ icon: faArrowLeft })}
                />
            </div>
            <div
                className={Classes.RUNNING_TEXT}
                style={{
                    padding: 20,
                    overflowY: "auto",
                }}
            >
                <div style={{ marginBottom: 20 }}>
                    <H1 style={{ margin: 0 }}>Basics</H1>
                </div>
                <Callout intent={Intent.PRIMARY} icon={null}>
                    This is not a type, but a documentation. For full
                    documentation, please click&nbsp;
                    <a
                        rel="noreferrer"
                        target="_blank"
                        href="https://jsonforms.io/"
                    >
                        here
                    </a>
                    .
                </Callout>
                <H2>Controls</H2>
                <div>
                    Controls represent the basic building blocks for creating
                    forms.
                </div>
                <div>
                    A control is usually displaying the value of one property
                    from the data in an UI element such as an input field.
                </div>
                <div>
                    How a control is rendered depends on the type of the
                    property as defined in the JSON Schema, e.g. a property of
                    type boolean is rendered as a Checkbox by default.
                </div>
                <H3>scope &#40;string&#41;</H3>
                <div>
                    The mandatory <Code>scope</Code> property, which expects
                    a&nbsp;
                    <a
                        rel="noreferrer"
                        target="_blank"
                        href="https://json-schema.org/understanding-json-schema/structuring"
                    >
                        JSON schema reference value
                    </a>
                    , defines to which property of the data the control should
                    be bound to. For instance, let&apos;s suppose we want to
                    create a control for the name property in this schema:
                </div>
                <Pre>
                    <JsonViewer
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
                        json={{
                            type: "Control",
                            scope: "#/properties/name",
                        }}
                    />
                </Pre>
            </div>
        </>
    );
}

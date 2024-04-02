import Editor from "@/components/Editor";
import { faIcon } from "@/components/icon";
import BooleanRenderer, {
    BooleanTester,
} from "@/components/jsonforms/renderers/Boolean";
import ButtonRenderer, {
    ButtonTester,
} from "@/components/jsonforms/renderers/Button";
import EnumRenderer, {
    EnumTester,
} from "@/components/jsonforms/renderers/Enum";
import GroupRenderer, {
    GroupTester,
} from "@/components/jsonforms/renderers/Group";
import IntegerRenderer, {
    IntegerTester,
} from "@/components/jsonforms/renderers/Integer";
import LabelRenderer, {
    LabelTester,
} from "@/components/jsonforms/renderers/Label";
import LayoutRenderer, {
    LayoutTester,
} from "@/components/jsonforms/renderers/Layout";
import NumberRenderer, {
    NumberTester,
} from "@/components/jsonforms/renderers/Number";
import StringRenderer, {
    StringTester,
} from "@/components/jsonforms/renderers/String";
import UnknownRenderer, {
    UnknownTester,
} from "@/components/jsonforms/renderers/Unknown";
import { Alignment, Button, Callout } from "@blueprintjs/core";
import { faArrowsFromLine } from "@fortawesome/pro-duotone-svg-icons";
import { JsonForms } from "@jsonforms/react";
import { vanillaCells, vanillaRenderers } from "@jsonforms/vanilla-renderers";
import { Allotment } from "allotment";
import { createRef, useEffect, useState } from "react";
export default function Designer() {
    const topPaneRef = createRef();
    const [uiSchema, setUiSchema] = useState("{}");
    const [schema, setSchema] = useState("{}");
    const [data, setData] = useState({});
    const [jsonUiSchema, setJsonUiSchema] = useState({});
    const [jsonSchema, setJsonSchema] = useState({});
    const [uiSchemaError, setUiSchemaError] = useState(false);
    const [schemaError, setSchemaError] = useState(false);
    useEffect(() => {
        try {
            setJsonUiSchema(JSON.parse(uiSchema));
        } catch (error) {}
        try {
            setJsonSchema(JSON.parse(schema));
        } catch (error) {}
    }, [uiSchema, schema]);
    const BUTTON_PROPS = {
        alignText: Alignment.LEFT,
        fill: true,
        minimal: true,
        style: { fontWeight: 600 },
    };
    return (
        <Allotment>
            <Allotment.Pane minSize={321.094}>
                <Allotment vertical ref={topPaneRef}>
                    <Allotment.Pane minSize={187.5}>
                        <div
                            style={{
                                padding: 5,
                                borderBottom:
                                    "1px solid rgba(17, 20, 24, 0.15)",
                            }}
                        >
                            <Button
                                {...BUTTON_PROPS}
                                text="UI Schema"
                                onClick={() => {
                                    topPaneRef.current.resize([
                                        window.innerHeight,
                                        187.5,
                                    ]);
                                }}
                                rightIcon={faIcon({ icon: faArrowsFromLine })}
                            />
                        </div>
                        <div
                            className="full-parent-height"
                            style={{
                                overflowY: "auto",
                                maxHeight: "calc(100% - 41px)",
                            }}
                        >
                            <Editor
                                allowSaveWithError
                                code={uiSchema}
                                setCode={setUiSchema}
                                setError={setUiSchemaError}
                            />
                        </div>
                    </Allotment.Pane>
                    <Allotment.Pane minSize={187.5}>
                        <div
                            style={{
                                padding: 5,
                                borderBottom:
                                    "1px solid rgba(17, 20, 24, 0.15)",
                            }}
                        >
                            <Button
                                {...BUTTON_PROPS}
                                text="Schema"
                                onClick={() => {
                                    topPaneRef.current.resize([
                                        187.5,
                                        window.innerHeight,
                                    ]);
                                }}
                                rightIcon={faIcon({ icon: faArrowsFromLine })}
                            />
                        </div>

                        <div
                            className="full-parent-height"
                            style={{
                                overflowY: "auto",
                                maxHeight: "calc(100% - 41px)",
                            }}
                        >
                            <Editor
                                allowSaveWithError
                                code={schema}
                                setCode={setSchema}
                                setError={setSchemaError}
                            />
                        </div>
                    </Allotment.Pane>
                </Allotment>
            </Allotment.Pane>
            <Allotment.Pane minSize={187.5}>
                <div
                    className="full-parent-height"
                    style={{ padding: 20, overflowY: "auto" }}
                >
                    <Callout
                        style={{
                            width: 802.2,
                            whiteSpace: "pre-wrap",
                            maxWidth: "fit-content",
                        }}
                    >
                        <JsonForms
                            schema={jsonSchema}
                            uischema={jsonUiSchema}
                            data={data}
                            renderers={[
                                ...vanillaRenderers,
                                {
                                    tester: GroupTester,
                                    renderer: GroupRenderer,
                                },
                                {
                                    tester: LabelTester,
                                    renderer: LabelRenderer,
                                },
                                {
                                    tester: BooleanTester,
                                    renderer: BooleanRenderer,
                                },
                                { tester: EnumTester, renderer: EnumRenderer },
                                {
                                    tester: LayoutTester,
                                    renderer: LayoutRenderer,
                                },
                                {
                                    tester: StringTester,
                                    renderer: StringRenderer,
                                },
                                {
                                    tester: NumberTester,
                                    renderer: NumberRenderer,
                                },
                                {
                                    tester: IntegerTester,
                                    renderer: IntegerRenderer,
                                },
                                {
                                    tester: ButtonTester,
                                    renderer: ButtonRenderer,
                                },
                                {
                                    tester: UnknownTester,
                                    renderer: UnknownRenderer,
                                },
                            ]}
                            cells={vanillaCells}
                            onChange={({ data, errors }) => {
                                console.log(data, errors);
                                setData(data);
                            }}
                        />
                    </Callout>
                </div>
            </Allotment.Pane>
        </Allotment>
    );
}

import JsonEditor from "@/components/codemirror/JsonEditor";
import {
    Classes,
    H5,
    Intent,
    Section,
    SectionCard,
    Tag,
} from "@blueprintjs/core";
import { faBracketsCurly } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { faIcon } from "../icon";
import JsonViewer from "../sessions/message/renderers/JsonViewer";
export default function EntityProperties({
    entity,
    edit,
    setEdit,
    jsonError,
    setJsonError,
    updateEntity,
    loading,
    allowPopulateOnce = false,
}) {
    const setProperties = (value) => {
        updateEntity({ path: "properties", value: JSON.parse(value) });
    };
    return (
        <Section
            compact
            icon={faIcon({ icon: faBracketsCurly })}
            title={<H5 className="margin-0">Properties</H5>}
            style={{ marginTop: 20 }}
            rightElement={
                jsonError && edit ? (
                    <Tag large minimal intent={Intent.DANGER}>
                        Invalid JSON
                    </Tag>
                ) : null
            }
        >
            <SectionCard
                padded={false}
                onDoubleClick={(event) => {
                    if (_.isFunction(setEdit)) {
                        setEdit(true);
                    }
                    event.stopPropagation();
                }}
            >
                {loading ? (
                    <div style={{ margin: 15 }} className={Classes.SKELETON}>
                        &nbsp;
                    </div>
                ) : !edit ? (
                    <div style={{ padding: 15 }}>
                        <JsonViewer json={entity.properties} />
                    </div>
                ) : (
                    <JsonEditor
                        allowPopulateOnce={allowPopulateOnce}
                        code={JSON.stringify(entity.properties, null, 4)}
                        setCode={setProperties}
                        setError={setJsonError}
                        useMinimap={false}
                        containOverscrollBehavior={false}
                    />
                )}
            </SectionCard>
        </Section>
    );
}

import { faIcon } from "@/components/icon";
import {
    Classes,
    EditableText,
    H5,
    Section,
    SectionCard,
} from "@blueprintjs/core";
import { faQuoteLeft } from "@fortawesome/sharp-duotone-solid-svg-icons";
export default function EntityDescription({
    entity,
    edit,
    updateEntity,
    setEdit,
    loading = false,
}) {
    return (
        <Section
            compact
            icon={faIcon({ icon: faQuoteLeft })}
            title={<H5 className="margin-0">Description</H5>}
            style={{ marginTop: 20 }}
        >
            <SectionCard
                style={{ whiteSpace: !edit ? "pre-wrap" : null }}
                onDoubleClick={(event) => {
                    setEdit(true);
                    event.stopPropagation();
                }}
            >
                {loading ? (
                    <div className={Classes.SKELETON}>&nbsp;</div>
                ) : edit ? (
                    <EditableText
                        alwaysRenderInput
                        multiline
                        minLines={2}
                        onChange={(value) => {
                            updateEntity({ path: "description", value });
                        }}
                        value={entity.description}
                    />
                ) : (
                    entity.description
                )}
            </SectionCard>
        </Section>
    );
}

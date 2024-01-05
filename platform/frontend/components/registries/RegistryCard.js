import { Card, H5, Intent, Tag } from "@blueprintjs/core";
export default function RegistryCard({ title, description, extra }) {
    return (
        <Card interactive style={{ padding: 15, height: "100%" }}>
            <H5>{title}</H5>
            <div className="multiline-ellipsis">{description}</div>
            <Tag
                style={{ marginTop: 10 }}
                minimal
                intent={Intent.PRIMARY}
                interactive
            >
                {extra}
            </Tag>
        </Card>
    );
}

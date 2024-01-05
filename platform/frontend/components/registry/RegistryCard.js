import { Card, H5, Intent, Tag } from "@blueprintjs/core";
import Link from "next/link";
export default function RegistryCard({ title, description, href, extra }) {
    return (
        <Link href={href}>
            <Card interactive style={{ height: "100%" }}>
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
        </Link>
    );
}

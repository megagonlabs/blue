import { Card, Colors, H5, Intent, Tag } from "@blueprintjs/core";
import _ from "lodash";
import Link from "next/link";
export default function RegistryCard({ title, description, href, extra }) {
    return (
        <Link className="no-link-decoration" href={href}>
            <Card
                style={{
                    height: "100%",
                    backgroundColor: Colors.LIGHT_GRAY5,
                }}
            >
                <H5>{title}</H5>
                <div className="multiline-ellipsis">{description}</div>
                {!_.isEmpty(extra) ? (
                    <Tag
                        style={{ marginTop: 10 }}
                        large
                        minimal
                        intent={Intent.PRIMARY}
                    >
                        {extra}
                    </Tag>
                ) : null}
            </Card>
        </Link>
    );
}

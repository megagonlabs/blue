import {
    Button,
    Intent,
    Menu,
    MenuItem,
    OverflowList,
    Popover,
    Position,
    Tag,
} from "@blueprintjs/core";
import { faAngleRight, faBars } from "@fortawesome/pro-duotone-svg-icons";
import Link from "next/link";
import { faIcon } from "../icon";
export default function RegistryBreadcrumbs({ breadcrumbs }) {
    const HYPHEN_ICON = faIcon({
        icon: faAngleRight,
        style: { marginLeft: 10, marginRight: 10 },
    });
    const BREADCRUMB_STYLE = {
        display: "flex",
        alignItems: "center",
    };
    return (
        <OverflowList
            items={breadcrumbs}
            overflowRenderer={(items) => {
                return (
                    <Popover
                        position={Position.BOTTOM_LEFT}
                        content={
                            <Menu>
                                {_.reverse(items).map(
                                    ({ href, text, end }, index) => {
                                        if (end) return null;
                                        return (
                                            <Link
                                                href={href}
                                                key={`registry-breadcrumb-overflow-${index}`}
                                            >
                                                <MenuItem
                                                    intent={Intent.PRIMARY}
                                                    text={text}
                                                />
                                            </Link>
                                        );
                                    }
                                )}
                            </Menu>
                        }
                    >
                        <Button
                            intent={Intent.PRIMARY}
                            minimal
                            icon={faIcon({ icon: faBars })}
                        />
                    </Popover>
                );
            }}
            visibleItemRenderer={(item, index) => {
                const { href, text, start, end } = item;
                if (end) {
                    return (
                        <div
                            style={BREADCRUMB_STYLE}
                            key={`registry-breadcrumb-${index}`}
                        >
                            {!start || !end ? HYPHEN_ICON : null}
                            <Tag large minimal>
                                {text}
                            </Tag>
                        </div>
                    );
                }
                return (
                    <div
                        style={BREADCRUMB_STYLE}
                        key={`registry-breadcrumb-${index}`}
                    >
                        {!start ? HYPHEN_ICON : null}
                        <Link href={href}>
                            <Tag
                                large
                                minimal
                                interactive
                                intent={Intent.PRIMARY}
                            >
                                {text}
                            </Tag>
                        </Link>
                    </div>
                );
            }}
        />
    );
}

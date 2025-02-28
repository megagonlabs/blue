import { faIcon } from "@/components/icon";
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
import {
    faAngleRight,
    faBars,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import Link from "next/link";
export default function Breadcrumbs({ breadcrumbs }) {
    const HYPHEN_ICON = faIcon({
        icon: faAngleRight,
        style: { marginLeft: 5, marginRight: 5 },
    });
    const BREADCRUMB_STYLE = {
        display: "flex",
        alignItems: "center",
    };
    const TAG_PROPS = {
        size: "large",
        minimal: true,
    };
    return (
        <OverflowList
            items={breadcrumbs}
            overflowRenderer={(items) => (
                <Popover
                    position={Position.BOTTOM_LEFT}
                    content={
                        <Menu size="large">
                            {_.reverse(items).map(
                                ({ href, text, end, icon }, index) => {
                                    if (end) return null;
                                    if (_.isNil(href)) {
                                        return (
                                            <MenuItem
                                                key={index}
                                                icon={
                                                    !_.isEmpty(icon)
                                                        ? faIcon({
                                                              icon: icon,
                                                          })
                                                        : null
                                                }
                                                intent={Intent.PRIMARY}
                                                text={text}
                                            />
                                        );
                                    }
                                    return (
                                        <Link
                                            href={href}
                                            className="no-link-decoration"
                                            key={index}
                                        >
                                            <MenuItem
                                                icon={
                                                    !_.isEmpty(icon)
                                                        ? faIcon({
                                                              icon: icon,
                                                          })
                                                        : null
                                                }
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
            )}
            visibleItemRenderer={(item, index) => {
                const { href, text, start, end, icon } = item;
                if (end) {
                    return (
                        <div style={BREADCRUMB_STYLE} key={index}>
                            {!start || !end ? HYPHEN_ICON : null}
                            <Tag
                                {...TAG_PROPS}
                                icon={
                                    !_.isEmpty(icon)
                                        ? faIcon({ icon: icon })
                                        : null
                                }
                            >
                                {text}
                            </Tag>
                        </div>
                    );
                }
                return (
                    <div style={BREADCRUMB_STYLE} key={index}>
                        {!start ? HYPHEN_ICON : null}
                        {_.isNil(href) ? (
                            <Tag
                                {...TAG_PROPS}
                                icon={
                                    !_.isEmpty(icon)
                                        ? faIcon({ icon: icon })
                                        : null
                                }
                            >
                                {text}
                            </Tag>
                        ) : (
                            <Link href={href}>
                                <Tag
                                    {...TAG_PROPS}
                                    icon={
                                        !_.isEmpty(icon)
                                            ? faIcon({ icon: icon })
                                            : null
                                    }
                                    style={{ pointerEvents: "none" }}
                                    interactive
                                    intent={Intent.PRIMARY}
                                >
                                    {text}
                                </Tag>
                            </Link>
                        )}
                    </div>
                );
            }}
        />
    );
}

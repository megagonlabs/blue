import {
    Button,
    ButtonVariant,
    CompoundTag,
    Intent,
    OverflowList,
    Popover,
    Size,
} from "@blueprintjs/core";
import {
    faAngleRight,
    faBars,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
const { FAIcon } = require("../FAIcon");
const HYPHEN_ICON = (
    <FAIcon icon={faAngleRight} style={{ marginLeft: 5, marginRight: 5 }} />
);
const BREADCRUMB_STYLES = { display: "flex", alignItems: "center" };
const TAG_PROPS = { size: Size.LARGE, minimal: true };
export default function Breadcrumbs({ crumbs, toCrumb }) {
    return (
        <OverflowList
            items={crumbs}
            overflowRenderer={(items) => (
                <Popover
                    placement="bottom-start"
                    content={
                        <div
                            style={{
                                padding: 10,
                                display: "flex",
                                flexDirection: "column-reverse",
                                gap: 10,
                            }}
                        >
                            {items.map((item) => {
                                const { name, type, end, index } = item;
                                if (end) return null;
                                return (
                                    <CompoundTag
                                        {...TAG_PROPS}
                                        fill
                                        leftContent={type}
                                        intent={!end ? Intent.PRIMARY : null}
                                        onClick={
                                            !end
                                                ? () => {
                                                      toCrumb(index);
                                                  }
                                                : null
                                        }
                                        style={{
                                            cursor: !end ? "pointer" : null,
                                        }}
                                    >
                                        {name}
                                    </CompoundTag>
                                );
                            })}
                        </div>
                    }
                >
                    <Button
                        variant={ButtonVariant.MINIMAL}
                        icon={<FAIcon icon={faBars} />}
                        intent={Intent.PRIMARY}
                    />
                </Popover>
            )}
            visibleItemRenderer={(item) => {
                const { name, type, start, end, index } = item;
                return (
                    <div style={BREADCRUMB_STYLES}>
                        {!start ? HYPHEN_ICON : null}
                        <CompoundTag
                            {...TAG_PROPS}
                            leftContent={type}
                            intent={!end ? Intent.PRIMARY : null}
                            onClick={
                                !end
                                    ? () => {
                                          toCrumb(index);
                                      }
                                    : null
                            }
                            style={{ cursor: !end ? "pointer" : null }}
                        >
                            {name}
                        </CompoundTag>
                    </div>
                );
            }}
        />
    );
}

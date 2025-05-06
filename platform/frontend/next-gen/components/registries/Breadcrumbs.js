import { CompoundTag, OverflowList, Size } from "@blueprintjs/core";
import { faAngleRight } from "@fortawesome/sharp-duotone-solid-svg-icons";
const { FAIcon } = require("../FAIcon");
const HYPHEN_ICON = (
    <FAIcon icon={faAngleRight} style={{ marginLeft: 5, marginRight: 5 }} />
);
const BREADCRUMB_STYLES = { display: "flex", alignItems: "center" };
const TAG_PROPS = { size: Size.LARGE, minimal: true };
export default function Breadcrumbs({ crumbs }) {
    return (
        <OverflowList
            items={crumbs}
            visibleItemRenderer={(item) => {
                const { name, type, start, end } = item;
                return (
                    <div style={BREADCRUMB_STYLES}>
                        {!start ? HYPHEN_ICON : null}
                        <CompoundTag
                            {...TAG_PROPS}
                            leftContent={type}
                            interactive={!end}
                        >
                            {name}
                        </CompoundTag>
                    </div>
                );
            }}
        />
    );
}

import { useGridStore } from "@/stores/grid-layout-store";
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
import _ from "lodash";
import { useShallow } from "zustand/react/shallow";
import { ENTITY_TYPE_LOOKUP } from "../constants";
import { useGridContainerContext } from "../contexts/GridContainerContext";
const { FAIcon } = require("../FAIcon");
const HYPHEN_ICON = (
    <FAIcon icon={faAngleRight} style={{ marginLeft: 5, marginRight: 5 }} />
);
const BREADCRUMB_STYLES = { display: "flex", alignItems: "center" };
const TAG_PROPS = { size: Size.LARGE, minimal: true };
export default function Breadcrumbs({ crumbs, toCrumb }) {
    const { replaceContainer } = useGridStore(
        useShallow((state) => ({ replaceContainer: state.replaceContainer }))
    );
    const { gridContainerId } = useGridContainerContext();
    if (_.isEmpty(crumbs)) {
        return null;
    }
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
                                const {
                                    name,
                                    type,
                                    end,
                                    index,
                                    content,
                                    title,
                                } = item;
                                const icon = _.get(
                                    ENTITY_TYPE_LOOKUP,
                                    [item["listType"], "icon"],
                                    null
                                );
                                if (end) return null;
                                const onClick = () => {
                                    if (_.isEqual(type, "registry")) {
                                        replaceContainer({
                                            id: gridContainerId,
                                            content,
                                            icon,
                                            title,
                                        });
                                    } else {
                                        toCrumb(index);
                                    }
                                };
                                return (
                                    <CompoundTag
                                        key={index}
                                        {...TAG_PROPS}
                                        fill
                                        leftContent={type}
                                        intent={!end ? Intent.PRIMARY : null}
                                        onClick={!end ? onClick : null}
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
                const { name, type, start, end, index, content, title } = item;
                const icon = _.get(
                    ENTITY_TYPE_LOOKUP,
                    [item["listType"], "icon"],
                    null
                );
                const onClick = () => {
                    if (_.isEqual(type, "registry")) {
                        replaceContainer({
                            id: gridContainerId,
                            content,
                            icon,
                            title,
                        });
                    } else {
                        toCrumb(index);
                    }
                };
                return (
                    <div style={BREADCRUMB_STYLES}>
                        {!start ? HYPHEN_ICON : null}
                        <CompoundTag
                            {...TAG_PROPS}
                            leftContent={type}
                            intent={!end ? Intent.PRIMARY : null}
                            onClick={!end ? onClick : null}
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

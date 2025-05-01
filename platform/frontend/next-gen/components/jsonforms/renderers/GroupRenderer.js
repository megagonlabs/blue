import { FAIcon } from "@/components/FAIcon";
import { convertCss } from "@/components/helper";
import { Intent, Size, Tag } from "@blueprintjs/core";
import { faObjectGroup } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { rankWith, uiTypeIs } from "@jsonforms/core";
import { JsonFormsDispatch, withJsonFormsLayoutProps } from "@jsonforms/react";
import _ from "lodash";
const GroupRenderer = ({
    cells,
    path,
    renderers,
    schema,
    uischema,
    visible,
}) => {
    const label = _.get(uischema, "label", null);
    return (
        <div
            className="custom-card"
            collapseProps={{
                defaultIsOpen: _.get(uischema, "props.defaultIsOpen", true),
            }}
            style={convertCss({
                ..._.get(uischema, "props.style", {}),
                maxWidth: "100%",
                overflow: "auto",
            })}
            compact={_.get(uischema, "props.compact", false)}
            collapsible={_.get(uischema, "props.collapsible", false)}
        >
            <div style={{ padding: "10px 20px 10px 10px" }}>
                <Tag
                    minimal
                    style={{
                        backgroundColor: "transparent",
                        fontWeight: 600,
                    }}
                    size={Size.LARGE}
                    intent={Intent.PRIMARY}
                    icon={
                        <FAIcon
                            icon={faObjectGroup}
                            style={{ marginRight: 10 }}
                        />
                    }
                >
                    {_.isString(label) ? label : null}
                </Tag>
            </div>
            <div
                style={{
                    padding: "0px 20px 20px",
                    display: "flex",
                    flexDirection: "column",
                }}
            >
                {visible &&
                    !_.isEmpty(uischema.elements) &&
                    uischema.elements.map((child, index) => {
                        return (
                            <JsonFormsDispatch
                                schema={schema}
                                uischema={child}
                                path={path}
                                renderers={renderers}
                                cells={cells}
                                key={index}
                            />
                        );
                    })}
            </div>
        </div>
    );
};
export default withJsonFormsLayoutProps(GroupRenderer);
export const GroupTester = rankWith(3, uiTypeIs("Group"));

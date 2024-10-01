import { convertCss } from "@/components/helper";
import { Section, SectionCard } from "@blueprintjs/core";
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
        <Section
            collapseProps={{
                defaultIsOpen: _.get(uischema, "props.defaultIsOpen", true),
            }}
            style={convertCss(_.get(uischema, "props.style", {}))}
            compact={_.get(uischema, "props.compact", false)}
            collapsible={_.get(uischema, "props.collapsible", false)}
            title={_.isString(label) ? label : null}
        >
            <SectionCard style={{ display: "flex", flexDirection: "column" }}>
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
            </SectionCard>
        </Section>
    );
};
export default withJsonFormsLayoutProps(GroupRenderer);
export const GroupTester = rankWith(3, uiTypeIs("Group"));

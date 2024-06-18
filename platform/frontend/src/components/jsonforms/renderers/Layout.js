import { or, rankWith, uiTypeIs } from "@jsonforms/core";
import { JsonFormsDispatch, withJsonFormsLayoutProps } from "@jsonforms/react";
import _ from "lodash";
const LayoutRenderer = ({
    cells,
    path,
    renderers,
    schema,
    uischema,
    visible,
    direction,
}) => {
    // default layout is VerticalLayout
    const type = _.get(uischema, "type", "VerticalLayout");
    const spaceEvenly = _.get(uischema, "props.spaceEvenly", true);
    const isHorizontal = _.isEqual(type, "HorizontalLayout");
    return (
        <div
            style={{
                display: "flex",
                flexDirection: direction,
                columnGap: 15,
            }}
        >
            {visible &&
                !_.isEmpty(uischema.elements) &&
                uischema.elements.map((child, index) => {
                    return (
                        <div
                            key={index}
                            style={
                                isHorizontal && spaceEvenly ? { flex: 1 } : null
                            }
                        >
                            <JsonFormsDispatch
                                schema={schema}
                                uischema={child}
                                path={path}
                                renderers={renderers}
                                cells={cells}
                                key={index}
                            />
                        </div>
                    );
                })}
        </div>
    );
};
export default withJsonFormsLayoutProps(LayoutRenderer);
export const LayoutTester = rankWith(
    3,
    or(uiTypeIs("HorizontalLayout"), uiTypeIs("VerticalLayout"))
);

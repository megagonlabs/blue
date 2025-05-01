import { convertCss } from "@/components/helper";
import { rankWith, uiTypeIs } from "@jsonforms/core";
import { withJsonFormsCellProps } from "@jsonforms/react";
import _ from "lodash";
const { Button, Size, ButtonVariant } = require("@blueprintjs/core");
const ButtonRenderer = ({ uischema, path }) => {
    const onClickHandler = () => {};
    return (
        <Button
            ellipsizeText
            onClick={onClickHandler}
            variant={
                _.get(uischema, "props.outlined", false)
                    ? ButtonVariant.OUTLINED
                    : null
            }
            style={convertCss(_.get(uischema, "props.style", {}))}
            size={_.get(uischema, "props.large", false) ? Size.LARGE : null}
            intent={_.get(uischema, "props.intent", null)}
            text={_.get(uischema, "label", null)}
        />
    );
};
export default withJsonFormsCellProps(ButtonRenderer);
export const ButtonTester = rankWith(3, uiTypeIs("Button"));

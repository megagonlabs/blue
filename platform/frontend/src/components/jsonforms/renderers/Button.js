import { rankWith, uiTypeIs } from "@jsonforms/core";
import { withJsonFormsCellProps } from "@jsonforms/react";
import _ from "lodash";
const { Button } = require("@blueprintjs/core");
const ButtonRenderer = ({ uischema }) => {
    const onClickHandler = () => {};
    return (
        <Button
            onClick={onClickHandler}
            large={_.get(uischema, "props.large", false)}
            intent={_.get(uischema, "props.intent", null)}
            text={_.get(uischema, "text", null)}
        />
    );
};
export default withJsonFormsCellProps(ButtonRenderer);
export const ButtonTester = rankWith(3, uiTypeIs("Button"));

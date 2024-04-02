import { AppContext } from "@/components/app-context";
import { rankWith, uiTypeIs } from "@jsonforms/core";
import { withJsonFormsCellProps } from "@jsonforms/react";
import _ from "lodash";
import { useContext } from "react";
const { Button } = require("@blueprintjs/core");
const ButtonRenderer = ({ uischema }) => {
    const { appState } = useContext(AppContext);
    const onClickHandler = () => {
        if (_.isNil(appState.session.connection)) return;
        setTimeout(() => {
            appState.session.connection.send(
                JSON.stringify({
                    type: "INTERACTIVE_EVENT_MESSAGE",
                    stream_id: _.get(uischema, "props.streamId", null),
                    name_id: _.get(uischema, "props.nameId", null),
                    message: _.get(uischema, "props.action", null),
                    timestamp: Date.now(),
                })
            );
        }, 0);
    };
    return (
        <Button
            onClick={onClickHandler}
            style={_.get(uischema, "props.style", {})}
            large={_.get(uischema, "props.large", false)}
            intent={_.get(uischema, "props.intent", null)}
            text={_.get(uischema, "text", null)}
        />
    );
};
export default withJsonFormsCellProps(ButtonRenderer);
export const ButtonTester = rankWith(3, uiTypeIs("Button"));

import { useSocket } from "@/components/hooks/useSocket";
import { rankWith, uiTypeIs } from "@jsonforms/core";
import { withJsonFormsCellProps } from "@jsonforms/react";
import _ from "lodash";
const { Button } = require("@blueprintjs/core");
const ButtonRenderer = ({ uischema }) => {
    const { socket } = useSocket();
    const socketReadyState = _.get(socket, "readyState", 3);
    const onClickHandler = () => {
        if (!_.isEqual(socketReadyState, 1)) {
            return;
        }
        setTimeout(() => {
            const dataId = _.last(_.split(_.get(uischema, "scope", ""), "/"));
            socket.send(
                JSON.stringify({
                    type: "INTERACTIVE_EVENT_MESSAGE",
                    stream_id: _.get(uischema, "props.streamId", null),
                    name_id: _.get(uischema, "props.nameId", dataId),
                    form_id: _.get(uischema, "props.formId", null),
                    timestamp: Date.now(),
                })
            );
        }, 0);
    };
    return (
        <Button
            onClick={onClickHandler}
            outlined={_.get(uischema, "props.outlined", false)}
            style={_.get(uischema, "props.style", {})}
            large={_.get(uischema, "props.large", false)}
            intent={_.get(uischema, "props.intent", null)}
            text={_.get(uischema, "label", null)}
        />
    );
};
export default withJsonFormsCellProps(ButtonRenderer);
export const ButtonTester = rankWith(3, uiTypeIs("Button"));

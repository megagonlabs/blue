import { convertCss } from "@/components/helper";
import { useSocketStore } from "@/stores/socket-store";
import { rankWith, uiTypeIs } from "@jsonforms/core";
import { withJsonFormsCellProps } from "@jsonforms/react";
import _ from "lodash";
const { Button, Size, ButtonVariant } = require("@blueprintjs/core");
const ButtonRenderer = ({ uischema, path }) => {
    const sendMessage = useSocketStore((state) => state.sendMessage);
    const onClickHandler = () => {
        setTimeout(() => {
            sendMessage(
                JSON.stringify({
                    type: "INTERACTIVE_EVENT_MESSAGE",
                    stream_id: _.get(uischema, "props.streamId", null),
                    path,
                    action: _.get(uischema, "props.action", null),
                    form_id: _.get(uischema, "props.formId", null),
                    timestamp: performance.timeOrigin + performance.now(),
                })
            );
        }, 0);
    };
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

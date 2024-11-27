import { sendSocketMessage } from "@/components/helper";
import { useSocket } from "@/components/hooks/useSocket";
import { Button, ButtonGroup, Callout, Card, Intent } from "@blueprintjs/core";
import { rankWith, uiTypeIs } from "@jsonforms/core";
import { JsonFormsDispatch, withJsonFormsControlProps } from "@jsonforms/react";
import _ from "lodash";
import { useState } from "react";
const TabsRenderer = ({
    cells,
    path,
    data,
    handleChange,
    renderers,
    schema,
    uischema,
    visible,
}) => {
    const { socket } = useSocket();
    const tabs = _.get(uischema, "tabs");
    const [activeTab, setActiveTab] = useState(_.isNumber(data) ? data : 0);
    if (_.size(tabs) != _.size(uischema.elements))
        return (
            <Callout intent={Intent.DANGER} icon={null}>
                Number of tabs doesn&apos;t match the number of elements.
                <br />
                {_.size(tabs)} tabs, {_.size(uischema.elements)} elements.
            </Callout>
        );
    const handleTabChange = (tabIndex) => {
        if (!_.isEmpty(path)) handleChange(path, tabIndex);
        if (!_.isEqual(socket.readyState, WebSocket.OPEN)) return;
        setTimeout(() => {
            sendSocketMessage(
                socket,
                JSON.stringify({
                    type: "INTERACTIVE_EVENT_MESSAGE",
                    stream_id: _.get(uischema, "props.streamId", null),
                    path: path,
                    form_id: _.get(uischema, "props.formId", null),
                    value: tabIndex,
                    timestamp: performance.timeOrigin + performance.now(),
                })
            );
        }, 0);
    };
    const style = _.get(uischema, "props.style", {});
    const large = _.get(uischema, "props.large", false);
    const compact = _.get(uischema, "props.compact", false);
    const vertical = _.get(uischema, "props.vertical", false);
    const TAB_STYLE = !vertical
        ? {
              padding: `5px ${compact ? 15 : 20}px`,
              overflowX: "auto",
              marginBottom: 15,
              overscrollBehavior: "contain",
          }
        : { padding: 5 };
    return (
        <div
            style={{
                ...(vertical
                    ? { display: "flex", gap: 15, alignItems: "flex-start" }
                    : {}),
                ...style,
            }}
        >
            <Card style={{ ...TAB_STYLE }}>
                <ButtonGroup vertical={vertical} minimal large={large}>
                    {tabs.map((tab, index) => (
                        <Button
                            key={index}
                            onClick={() => {
                                setActiveTab(index);
                                handleTabChange(index);
                            }}
                            active={_.isEqual(activeTab, index)}
                            text={tab}
                        />
                    ))}
                </ButtonGroup>
            </Card>
            {visible &&
                !_.isEmpty(uischema.elements) &&
                uischema.elements.map((child, index) => {
                    return (
                        <div
                            key={index}
                            style={{
                                display: _.isEqual(activeTab, index)
                                    ? null
                                    : "none",
                            }}
                        >
                            <JsonFormsDispatch
                                schema={schema}
                                uischema={child}
                                path={path}
                                renderers={renderers}
                                cells={cells}
                            />
                        </div>
                    );
                })}
        </div>
    );
};
export default withJsonFormsControlProps(TabsRenderer);
export const TabsTester = rankWith(3, uiTypeIs("Tabs"));

import {
    EMPTY_ARRAY,
    HEX_TRANSPARENCY,
    POPOVER_CONTENT_MAX_WIDTH,
} from "@/components/constants";
import { useReactFlowCustomContext } from "@/components/contexts/ReactFlowCustomContext";
import { useAppStore } from "@/stores/app-store";
import { Classes, Colors, Intent, Tag, Tooltip } from "@blueprintjs/core";
import { Handle, Position } from "@xyflow/react";
import classNames from "classnames";
import _ from "lodash";
import BaseNode from "./BaseNode";
const renderHandles = (handles, type, position, isVertical) => {
    if (_.isEmpty(handles)) return null;
    let handleStyle = {
        paddingTop: isVertical && type === "target" ? 5 : null,
        paddingLeft: !isVertical && type === "target" ? 7 : null,
        paddingBottom: isVertical && type === "source" ? 5 : null,
        paddingRight: !isVertical && type === "source" ? 7 : null,
        display: "flex",
        alignItems: "center",
        maxWidth: isVertical || type === "target" ? 125 : null,
    };
    if (!isVertical) {
        if (type === "target") {
            handleStyle["textAlign"] = "left";
        } else if (type === "source") {
            handleStyle["textAlign"] = "right";
        }
    }
    return handles.map((handleName) => {
        return (
            <div
                className={classNames("position-relative", Classes.TEXT_MUTED, {
                    "full-parent-width": !isVertical,
                })}
                key={`${type}-${handleName}`}
                style={handleStyle}
            >
                <Handle id={handleName} type={type} position={position} />
                <Tooltip className="full-parent-width" content={handleName}>
                    <div className={Classes.TEXT_OVERFLOW_ELLIPSIS}>
                        {handleName}
                    </div>
                </Tooltip>
            </div>
        );
    });
};
export default function AgentNode({ id, data }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const { inputs = EMPTY_ARRAY, outputs = EMPTY_ARRAY } = data;
    const { direction } = useReactFlowCustomContext();
    const isVertical = _.isEqual(direction, "TB");
    return (
        <BaseNode id={id} data={data}>
            {isVertical && !_.isEmpty(inputs) && (
                <div
                    style={{
                        display: "flex",
                        padding: "20px 10px 5px",
                        justifyContent: "space-evenly",
                        gap: 10,
                        backgroundColor: `${Colors.GRAY5}${HEX_TRANSPARENCY[15]}`,
                        borderColor: darkMode
                            ? `${Colors.WHITE}${HEX_TRANSPARENCY[20]}`
                            : `${Colors.BLACK}${HEX_TRANSPARENCY[15]}`,
                    }}
                    className="border-bottom"
                >
                    {renderHandles(inputs, "target", Position.Top, true)}
                </div>
            )}
            <div className="position-relative" style={{ padding: 10 }}>
                <div
                    className="map-pin"
                    style={{ position: "absolute", right: 10, top: 10 }}
                />
                <Tag
                    intent={Intent.PRIMARY}
                    minimal
                    style={{ marginBottom: 10 }}
                >
                    Agent
                </Tag>
                <div style={{ height: 18 }}>
                    <Tooltip
                        className="full-parent-width"
                        content={
                            <div
                                style={{
                                    maxWidth: POPOVER_CONTENT_MAX_WIDTH,
                                    wordBreak: "break-all",
                                }}
                            >
                                {data.label}
                            </div>
                        }
                    >
                        <div className={Classes.TEXT_OVERFLOW_ELLIPSIS}>
                            {data.label}
                        </div>
                    </Tooltip>
                </div>
            </div>
            {isVertical
                ? !_.isEmpty(outputs) && (
                      <div
                          style={{
                              display: "flex",
                              padding: "5px 10px 10px",
                              justifyContent: "space-evenly",
                              gap: 10,
                              backgroundColor: `${Colors.GRAY5}${HEX_TRANSPARENCY[15]}`,
                              borderColor: darkMode
                                  ? `${Colors.WHITE}${HEX_TRANSPARENCY[20]}`
                                  : `${Colors.BLACK}${HEX_TRANSPARENCY[15]}`,
                          }}
                          className="border-top"
                      >
                          {renderHandles(
                              outputs,
                              "source",
                              Position.Bottom,
                              true
                          )}
                      </div>
                  )
                : (!_.isEmpty(inputs) || !_.isEmpty(outputs)) && (
                      <div
                          className="border-top"
                          style={{
                              maxWidth: POPOVER_CONTENT_MAX_WIDTH,
                              display: "flex",
                              padding: 10,
                              gap: 10,
                              backgroundColor: `${Colors.GRAY5}${HEX_TRANSPARENCY[15]}`,
                          }}
                      >
                          <div
                              style={{
                                  maxWidth: 135,
                                  display: "flex",
                                  gap: 5,
                                  flexDirection: "column",
                                  alignItems: "flex-start",
                                  flex: "1 0 auto",
                              }}
                          >
                              {!_.isEmpty(inputs) && (
                                  <>
                                      <div
                                          className={classNames(
                                              Classes.TEXT_DISABLED,
                                              Classes.TEXT_SMALL
                                          )}
                                      >
                                          INPUTS
                                      </div>
                                      <div
                                          className="full-parent-dimension"
                                          style={{
                                              padding: "0px 0px 0px 10px",
                                          }}
                                      >
                                          {renderHandles(
                                              inputs,
                                              "target",
                                              Position.Left,
                                              false
                                          )}
                                      </div>
                                  </>
                              )}
                          </div>
                          <div
                              style={{
                                  maxWidth: 135,
                                  display: "flex",
                                  gap: 5,
                                  flexDirection: "column",
                                  alignItems: "flex-end",
                                  flex: "1 0 auto",
                              }}
                          >
                              {!_.isEmpty(outputs) && (
                                  <>
                                      <div
                                          className={classNames(
                                              Classes.TEXT_DISABLED,
                                              Classes.TEXT_SMALL
                                          )}
                                      >
                                          OUTPUTS
                                      </div>
                                      {renderHandles(
                                          outputs,
                                          "source",
                                          Position.Right,
                                          false
                                      )}
                                  </>
                              )}
                          </div>
                      </div>
                  )}
        </BaseNode>
    );
}

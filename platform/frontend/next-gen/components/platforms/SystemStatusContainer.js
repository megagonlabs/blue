import { useAppStore } from "@/stores/app-store";
import { useSystemStatusStore } from "@/stores/system-status-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Classes,
    Colors,
    InputGroup,
    Menu,
    MenuItem,
    NonIdealState,
    Popover,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import {
    faFastForward,
    faMonitorWaveform,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { faSearch } from "@fortawesome/sharp-solid-svg-icons";
import _ from "lodash";
import { memo, useCallback, useMemo, useRef, useState } from "react";
import { Virtuoso } from "react-virtuoso";
import { useShallow } from "zustand/react/shallow";
import {
    CIRCLE_DOT_WITH_FADE,
    EMPTY_ARRAY,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
    VIRTUOSO_PROPS,
} from "../constants";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import NoResultsFound from "../nonidealstates/NoResultsFound";
const TrackerCard = memo(function TrackerCard({ index, message }) {
    const tracker = message;
    const { trackers, trackerData } = useSystemStatusStore(
        useShallow((state) => ({
            trackers: state.trackers,
            trackerData: state.trackerData,
        }))
    );
    const contents = _.get(trackerData, [tracker, "data"], EMPTY_ARRAY);
    const darkMode = useAppStore((state) => state.dark_mode);
    return (
        <div
            style={{
                padding: 20,
                paddingBottom: _.isEqual(index, _.size(trackers) - 1) ? 20 : 0,
            }}
        >
            <div
                style={{
                    borderRadius: 2,
                    padding: 20,
                    backgroundColor: darkMode
                        ? Colors.DARK_GRAY1
                        : Colors.LIGHT_GRAY5,
                }}
            >
                {contents.map((element, index) => (
                    <div key={index}>{element}</div>
                ))}
            </div>
        </div>
    );
});
function SystemStatusContainer({ width, height }) {
    const virtuosoRef = useRef(null);
    const darkMode = useAppStore((state) => state.dark_mode);
    const { trackers, isSystemStatusLive } = useSystemStatusStore(
        useShallow((state) => ({
            trackers: state.trackers,
            isSystemStatusLive: state.live,
        }))
    );
    const elementRef = useRef(null);
    const [keywords, setKeywords] = useState("");
    const filteredTrackers = useMemo(
        () =>
            trackers.filter((tracker) =>
                _.toLower(tracker).includes(_.toLower(keywords))
            ),
        [keywords, trackers]
    );
    const scrollToTracker = (tracker) => {
        virtuosoRef.current?.scrollToIndex({
            index: _.indexOf(trackers, tracker),
            align: "start",
            behavior: "auto",
        });
    };
    const popoverBoundary =
        elementRef.current &&
        elementRef.current.closest(".grid-container-boundary");
    const itemContent = useCallback(
        (index, message) => <TrackerCard index={index} message={message} />,
        []
    );
    return (
        <div
            ref={elementRef}
            style={{
                width,
                height,
                backgroundColor: darkMode ? Colors.BLACK : null,
            }}
        >
            <div className="border-bottom" style={{ padding: 10 }}>
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
                    {isSystemStatusLive && (
                        <Button
                            className="pointer-events-none"
                            icon={CIRCLE_DOT_WITH_FADE}
                        />
                    )}
                    <Popover
                        {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                        boundary={popoverBoundary}
                        minimal
                        content={
                            <div style={{ padding: 10, width: 400 }}>
                                <InputGroup
                                    value={keywords}
                                    onValueChange={(value) =>
                                        setKeywords(value)
                                    }
                                    leftIcon={<FAIcon icon={faSearch} />}
                                    size={Size.LARGE}
                                    style={{ marginBottom: 10 }}
                                />
                                {_.isEmpty(filteredTrackers) ? (
                                    <NoResultsFound />
                                ) : (
                                    <Menu style={{ padding: 0 }}>
                                        {filteredTrackers.map((tracker) => (
                                            <MenuItem
                                                key={tracker}
                                                className={
                                                    Classes.TEXT_OVERFLOW_ELLIPSIS
                                                }
                                                onClick={() =>
                                                    scrollToTracker(tracker)
                                                }
                                                text={tracker}
                                            />
                                        ))}
                                    </Menu>
                                )}
                            </div>
                        }
                    >
                        <Tooltip
                            {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                            content="Jump"
                            boundary={popoverBoundary}
                        >
                            <Button
                                disabled={_.isEmpty(trackers)}
                                icon={<FAIcon icon={faFastForward} />}
                            />
                        </Tooltip>
                    </Popover>
                </ButtonGroup>
            </div>
            <div
                className="full-parent-dimension"
                style={{ maxHeight: "calc(100% - 61px)" }}
            >
                {_.isEmpty(trackers) ? (
                    <NonIdealState
                        title="No Tracker"
                        description={
                            isSystemStatusLive &&
                            "Awaiting status messages. This could take some time."
                        }
                        icon={<FAIcon icon={faMonitorWaveform} size={50} />}
                    />
                ) : (
                    <Virtuoso
                        overscan={VIRTUOSO_PROPS.overscan}
                        computeItemKey={(index) => index}
                        ref={virtuosoRef}
                        data={trackers}
                        followOutput={false}
                        itemContent={itemContent}
                    />
                )}
            </div>
        </div>
    );
}
export default withAutoSizer(SystemStatusContainer);

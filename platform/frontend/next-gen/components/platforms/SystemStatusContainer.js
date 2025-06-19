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
    faCircleDot,
    faFastForward,
    faSearch,
    faWavePulse,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import { useShallow } from "zustand/react/shallow";
import {
    EMPTY_ARRAY,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "../constants";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import NoResultsFound from "../nonidealstates/NoResultsFound";
const TrackerCard = memo(function TrackerCard({ data, index, style }) {
    const { setRowHeight, rowHeights } = data;
    const cardRef = useRef();
    const { trackers, trackerData } = useSystemStatusStore(
        useShallow((state) => ({
            trackers: state.trackers,
            trackerData: state.trackerData,
        }))
    );
    const tracker = trackers[index];
    const contents = _.get(trackerData, [tracker, "data"], EMPTY_ARRAY);
    useEffect(() => {
        if (cardRef.current) {
            const newHeight = cardRef.current.getBoundingClientRect().height;
            if (!_.isEqual(rowHeights.current[index], newHeight)) {
                setRowHeight(index, newHeight);
            }
        }
    }, [index, setRowHeight, tracker]); // depend on 'tracker' instead of 'data' for more specific change detection
    return (
        <div
            style={{
                ...style,
                padding: "0px 20px",
                paddingTop: 20,
                paddingBottom: _.isEqual(index, _.size(trackers) - 1) ? 20 : 0,
            }}
        >
            <div ref={cardRef} className="custom-card" style={{ padding: 20 }}>
                {contents.map((element, index) => (
                    <div key={index}>{element}</div>
                ))}
            </div>
        </div>
    );
});
function SystemStatusContainer({ width, height }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const { trackers, isSystemStatusLive } = useSystemStatusStore(
        useShallow((state) => ({
            trackers: state.trackers,
            isSystemStatusLive: state.live,
        }))
    );
    const elementRef = useRef(null);
    const previousTrackersRef = useRef(trackers);
    const listRef = useRef(null);
    const rowHeights = useRef({});
    const firstVisibleIndex = useRef(0);
    const focusedTracker = useMemo(
        () => previousTrackersRef.current[firstVisibleIndex.current],
        [previousTrackersRef.current, firstVisibleIndex.current]
    );
    const trackerCardOffset = useRef(0);
    const setRowHeight = (index, size) => {
        // only update if the height is different to avoid unnecessary resets
        if (!_.isEqual(rowHeights.current[index], size)) {
            rowHeights.current = { ...rowHeights.current, [index]: size };
            // this is crucial: tell VariableSizeList to re-measure from this index onwards.
            // this ensures the list re-calculates its total height and item positions.
            if (listRef.current) {
                listRef.current.resetAfterIndex(index);
            }
        }
    };
    const getRowHeight = useCallback(
        (index) =>
            rowHeights.current[index] +
                20 +
                (_.isEqual(index, _.size(trackers) - 1) ? 20 : 0) || 69,
        [trackers]
    );
    const onScroll = ({ scrollOffset }) => {
        let topOffset = 0;
        for (let i = 0; i < firstVisibleIndex.current; i++) {
            topOffset += getRowHeight(i);
        }
        trackerCardOffset.current = scrollOffset - topOffset;
    };
    useEffect(() => {
        if (listRef.current) {
            listRef.current.resetAfterIndex(0);
            let topOffset = 0;
            let newFocusIndex = firstVisibleIndex.current;
            for (let i = 0; i < _.size(trackers); i++) {
                if (_.isEqual(trackers[i], focusedTracker)) {
                    newFocusIndex = i;
                    break;
                }
            }
            previousTrackersRef.current = trackers;
            for (let i = 0; i < newFocusIndex; i++) {
                topOffset += getRowHeight(i);
            }
            setTimeout(() => {
                listRef.current.scrollTo(topOffset + trackerCardOffset.current);
            }, 0);
        }
    }, [trackers, getRowHeight]);
    const [keywords, setKeywords] = useState("");
    const filteredTrackers = useMemo(
        () =>
            trackers.filter((tracker) =>
                _.toLower(tracker).includes(_.toLower(keywords))
            ),
        [keywords, trackers]
    );
    const scrollToTracker = (tracker) => {
        if (listRef.current) {
            let topOffset = 0;
            let targetIndex = 0;
            for (let i = 0; i < _.size(trackers); i++) {
                if (_.isEqual(trackers[i], tracker)) {
                    targetIndex = i;
                    break;
                }
            }
            for (let i = 0; i < targetIndex; i++) {
                topOffset += getRowHeight(i);
            }
            setTimeout(() => {
                listRef.current.scrollTo(topOffset);
            }, 0);
        }
    };
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
                            icon={
                                <FAIcon
                                    icon={faCircleDot}
                                    className="fa-fade"
                                    style={{
                                        "--fa-animation-duration": "2s",
                                        color: Colors.GREEN3,
                                    }}
                                />
                            }
                        />
                    )}
                    <Popover
                        {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                        boundary={elementRef.current}
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
                            boundary={elementRef.current}
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
                        icon={<FAIcon icon={faWavePulse} size={50} />}
                    />
                ) : (
                    <AutoSizer>
                        {({ height, width }) => (
                            <VariableSizeList
                                ref={listRef}
                                height={height}
                                width={width}
                                itemCount={_.size(trackers)}
                                itemSize={getRowHeight}
                                // itemData passes props to the individual Row components
                                itemData={{ setRowHeight, rowHeights }}
                                // onItemsRendered is used to track the first visible item's index
                                onItemsRendered={({ visibleStartIndex }) => {
                                    firstVisibleIndex.current =
                                        visibleStartIndex;
                                }}
                                onScroll={onScroll}
                            >
                                {TrackerCard}
                            </VariableSizeList>
                        )}
                    </AutoSizer>
                )}
            </div>
        </div>
    );
}
export default withAutoSizer(SystemStatusContainer);

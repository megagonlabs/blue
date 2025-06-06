import { useAppStore } from "@/stores/app-store";
import { useSystemStatusStore } from "@/stores/system-status-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Card,
    Colors,
    Divider,
    H5,
    NonIdealState,
    Size,
} from "@blueprintjs/core";
import {
    faCircleDot,
    faFastForward,
    faWavePulse,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { memo, useCallback, useEffect, useMemo, useRef } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
const TrackerCard = memo(({ data, index, style }) => {
    const { setRowHeight, rowHeights } = data;
    const cardRef = useRef();
    const { trackers, trackerData } = useSystemStatusStore(
        useShallow((state) => ({
            trackers: state.trackers,
            trackerData: state.trackerData,
        }))
    );
    const tracker = trackers[index];
    const contents = _.get(trackerData, [tracker, "data"], []);
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
            <Card ref={cardRef}>
                <H5>{index}</H5>
                {contents.map((element, index) => (
                    <div key={index}>{element}</div>
                ))}
            </Card>
        </div>
    );
});
function SystemStatusContainer({ width, height }) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const { trackers, isSystemStatusLive, addTracker } = useSystemStatusStore(
        useShallow((state) => ({
            trackers: state.trackers,
            isSystemStatusLive: state.live,
            addTracker: state.addTracker,
        }))
    );
    const listRef = useRef(null);
    const rowHeights = useRef({});
    const firstVisibleIndex = useRef(0);
    const previousTrackersRef = useRef(trackers);
    const trackerCardOffset = useRef(0);
    const focusedTracker = useMemo(() => {
        if (!_.isEmpty(previousTrackersRef.current)) {
            return previousTrackersRef.current[firstVisibleIndex.current];
        } else {
            return null;
        }
    }, [previousTrackersRef.current, firstVisibleIndex.current]);
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
        let offset = 0;
        for (let i = 0; i < firstVisibleIndex.current; i++) {
            offset += getRowHeight(i);
        }
        trackerCardOffset.current = scrollOffset - offset;
    };
    useEffect(() => {
        if (listRef.current) {
            listRef.current.resetAfterIndex(0);
            let topOffset = 0;
            let newVisibleIndex = firstVisibleIndex.current;
            for (let i = 0; i < _.size(trackers); i++) {
                if (_.isEqual(trackers[i], focusedTracker)) {
                    newVisibleIndex = i;
                }
            }
            for (let i = 0; i < newVisibleIndex; i++) {
                topOffset += getRowHeight(i);
            }
            previousTrackersRef.current = trackers;
            setTimeout(() => {
                listRef.current.scrollTo(topOffset + trackerCardOffset.current);
            }, 0);
        }
    }, [trackers, getRowHeight]);
    return (
        <div
            style={{
                width,
                height,
                backgroundColor: darkMode ? Colors.BLACK : null,
            }}
        >
            <div className="border-bottom" style={{ padding: 10 }}>
                <ButtonGroup size={Size.LARGE} variant={ButtonVariant.MINIMAL}>
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
                    <Divider />
                    <Button icon={<FAIcon icon={faFastForward} />} />
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

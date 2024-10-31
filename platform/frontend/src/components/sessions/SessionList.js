import { CARD_LIST_CLASS_NAMES } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import SessionRow from "@/components/sessions/SessionRow";
import _ from "lodash";
import { useContext, useEffect, useRef, useState } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList } from "react-window";
const Row = (props) => <SessionRow {...props} />;
export default function SessionList() {
    const { appState, appActions } = useContext(AppContext);
    const fixedSizeListRef = useRef();
    const { sessionGroupBy, sessionIds, pinnedSessionIds, sessionDetails } =
        appState.session;
    useEffect(() => {
        if (_.isEqual(sessionGroupBy, "pinned")) {
            appActions.session.setState({
                key: "groupedSessionIds",
                value: _.toArray(pinnedSessionIds).sort(
                    (a, b) =>
                        sessionDetails[b].created_date -
                        sessionDetails[a].created_date
                ),
            });
        } else {
            appActions.session.setState({
                key: "groupedSessionIds",
                value: sessionIds
                    .filter((sessionId) => {
                        const groupByFlag = _.get(
                            appState,
                            `session.sessionDetails.${sessionId}.group_by.${sessionGroupBy}`,
                            false
                        );
                        return _.isEqual(sessionGroupBy, "all") || groupByFlag;
                    })
                    .sort(
                        (a, b) =>
                            sessionDetails[b].created_date -
                            sessionDetails[a].created_date
                    ),
            });
        }
    }, [sessionGroupBy, sessionIds, pinnedSessionIds, sessionDetails]); // eslint-disable-line react-hooks/exhaustive-deps
    const [initialized, setInitialized] = useState(false);
    return (
        <>
            {!initialized && (
                <div className="border-right border-top full-parent-height" />
            )}
            <AutoSizer>
                {({ width, height }) => (
                    <FixedSizeList
                        onItemsRendered={() => {
                            setTimeout(() => {
                                if (_.isNil(fixedSizeListRef.current)) return;
                                try {
                                    const element = document.querySelectorAll(
                                        "div.session-list > div"
                                    )[0];
                                    if (
                                        _.isEqual(
                                            element.className,
                                            CARD_LIST_CLASS_NAMES
                                        )
                                    )
                                        return;
                                    element.className = CARD_LIST_CLASS_NAMES;
                                    setInitialized(true);
                                } catch (error) {
                                    // empty
                                }
                            }, 0);
                        }}
                        ref={fixedSizeListRef}
                        className={`session-list ${CARD_LIST_CLASS_NAMES}`}
                        style={{ borderRadius: 0, marginTop: 1 }}
                        height={height - 80 - 41}
                        width={width - 1}
                        itemCount={_.size(appState.session.groupedSessionIds)}
                        itemSize={82}
                    >
                        {Row}
                    </FixedSizeList>
                )}
            </AutoSizer>
        </>
    );
}

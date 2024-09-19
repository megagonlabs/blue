import { CARD_LIST_CLASS_NAMES } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import SessionRow from "@/components/sessions/SessionRow";
import _ from "lodash";
import { useContext, useEffect, useRef } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList } from "react-window";
const Row = (props) => <SessionRow {...props} />;
export default function SessionList() {
    const { appState, appActions } = useContext(AppContext);
    const fixedSizeListRef = useRef();
    const { sessionGroupBy, sessionIds } = appState.session;
    useEffect(() => {
        appActions.session.setState({
            key: "groupedSessionIds",
            value: sessionIds.filter((sessionId) => {
                const groupByFlag = _.get(
                    appState,
                    `session.sessionDetails.${sessionId}.group_by.${sessionGroupBy}`,
                    false
                );
                return _.isEqual(sessionGroupBy, "all") || groupByFlag;
            }),
        });
    }, [sessionGroupBy, sessionIds]);
    useEffect(() => {
        setTimeout(() => {
            if (_.isNil(fixedSizeListRef.current)) return;
            try {
                const element = document.querySelectorAll(
                    "div.session-list > div"
                )[0];
                if (_.isEqual(element.className, CARD_LIST_CLASS_NAMES)) return;
                element.className = CARD_LIST_CLASS_NAMES;
            } catch (error) {
                // empty
            }
        }, 0);
    }, [fixedSizeListRef]);
    return (
        <AutoSizer>
            {({ width, height }) => (
                <FixedSizeList
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
    );
}

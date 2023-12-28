import { Classes } from "@blueprintjs/core";
import { createRef, useContext, useEffect } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList } from "react-window";
import { AppContext } from "../app-context";
import SessionRow from "./SessionRow";
const Row = (props) => <SessionRow {...props} />;
export default function SessionList() {
    const cardListClassName = `${Classes.CARD} ${Classes.CARD_LIST} ${Classes.CARD_LIST_BORDERED}`;
    const { appState } = useContext(AppContext);
    const fixedSizeListRef = createRef();
    useEffect(() => {
        if (_.isNull(fixedSizeListRef)) return;
        try {
            const element = document.querySelectorAll(
                "div.session-list > div"
            )[0];
            if (_.isEqual(element.className, cardListClassName)) return;
            element.className = cardListClassName;
        } catch (error) {}
    }, [fixedSizeListRef]);
    return (
        <AutoSizer>
            {({ width, height }) => (
                <FixedSizeList
                    ref={fixedSizeListRef}
                    className={`session-list ${cardListClassName}`}
                    style={{ borderRadius: 0 }}
                    height={height}
                    width={width}
                    itemCount={appState.session.sessionIds.length}
                    itemSize={77}
                >
                    {Row}
                </FixedSizeList>
            )}
        </AutoSizer>
    );
}

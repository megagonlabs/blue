import { Classes } from "@blueprintjs/core";
import { useContext, useEffect, useRef } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList } from "react-window";
import { AppContext } from "../app-context";
import SessionRow from "./SessionRow";
const Row = (props) => <SessionRow {...props} />;
export default function SessionList() {
    const cardListClassName = `${Classes.CARD} ${Classes.CARD_LIST} ${Classes.CARD_LIST_BORDERED}`;
    const { appState } = useContext(AppContext);
    const fixedSizeListRef = useRef();
    useEffect(() => {
        setTimeout(() => {
            if (_.isNil(fixedSizeListRef.current)) return;
            try {
                const element = document.querySelectorAll(
                    "div.session-list > div"
                )[0];
                if (_.isEqual(element.className, cardListClassName)) return;
                element.className = cardListClassName;
            } catch (error) {}
        }, 0);
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
                    itemSize={87}
                >
                    {Row}
                </FixedSizeList>
            )}
        </AutoSizer>
    );
}

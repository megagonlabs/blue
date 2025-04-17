import { useAppStore } from "@/stores/app-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    ButtonVariant,
    Classes,
    Colors,
    ControlGroup,
    InputGroup,
    Intent,
    Radio,
    RadioGroup,
    Size,
} from "@blueprintjs/core";
import {
    faArrowLeft,
    faBarsFilter,
    faSearch,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { motion } from "framer-motion";
import _ from "lodash";
import { useEffect, useMemo, useRef, useState } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { VariableSizeList } from "react-window";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import SessionRow from "./SessionRow";
function SessionList({ width, height }) {
    const variants = {
        open: {
            x: 0,
            display: "block",
            transition: { duration: 0.15 },
        },
        closed: {
            x: -200,
            transition: { duration: 0.15 },
            display: "none",
        },
        initial: { x: -200, opacity: 1, display: "none" },
    };
    const darkMode = useAppStore((state) => state.darkMode);
    const { sessionIds, getSessions, sessions, filter, pinnedSessionIds } =
        useSessionStore(
            useShallow((state) => ({
                sessionIds: state.sessionIds,
                getSessions: state.getSessions,
                sessions: state.sessions,
                filter: state.filter,
                pinnedSessionIds: state.pinnedSessionIds,
            }))
        );
    const allSessions = useMemo(() => {
        let result = sessionIds
            .filter((id) => {
                const group = _.get(sessions, [
                    id,
                    "details",
                    "group_by",
                    filter.group,
                ]);
                return _.isEqual("all", filter.group) || group;
            })
            .filter((id) => {
                if (_.includes(id, filter.keyword)) return true;
                const name = _.get(sessions, [id, "details", "name"], id);
                if (_.includes(name, filter.keyword)) return true;
                const description = _.get(
                    sessions,
                    [id, "details", "description"],
                    id
                );
                if (_.includes(description, filter.keyword)) return true;
                return false;
            })
            .sort((l, r) => {
                let lPinned = pinnedSessionIds.has(l),
                    rPinned = pinnedSessionIds.has(r);
                return _.isEqual(lPinned, rPinned)
                    ? _.get(sessions, [r, "details", "created_date"]) -
                          _.get(sessions, [l, "details", "created_date"])
                    : rPinned - lPinned;
            });
        return [null, ...result];
    }, [sessionIds, filter, pinnedSessionIds, sessions]);
    const [showFilter, setShowFilter] = useState(false);
    useEffect(() => {
        getSessions();
    }, []);
    function getRowHeight(index, width) {
        const hasMessage = true;
        width -= 40; // left & right padding diff
        let height = 80;
        if (index > 0) {
            const last = _.isEqual(_.size(allSessions), index + 1);
            if (width < 768) {
                height = hasMessage ? 170 : 130;
            } else if (width < 992) {
                height = hasMessage ? 130 : 80;
            }
            return height + (last ? 10 : 0);
        }
        return height;
    }
    const variableSizeListRef = useRef();
    useEffect(() => {
        if (variableSizeListRef.current) {
            variableSizeListRef.current.resetAfterIndex(0);
        }
    }, [width]);
    return (
        <div style={{ width, height }}>
            <div
                className="full-parent-dimension"
                style={{
                    position: "relative",
                    overflowY: "auto",
                    backgroundColor: darkMode ? Colors.BLACK : null,
                }}
            >
                <motion.div
                    variants={variants}
                    initial="initial"
                    animate={showFilter ? "open" : "closed"}
                    className="full-parent-height border-right border-raidus-20"
                    style={{
                        position: "fixed",
                        maxHeight: "calc(100% - 45px)",
                        top: 45,
                        left: 0,
                        zIndex: 1,
                        padding: 20,
                        width: 200,
                        backgroundColor: darkMode
                            ? Colors.DARK_GRAY2
                            : Colors.WHITE,
                        overflowY: "auto",
                    }}
                >
                    <div
                        className={Classes.TEXT_LARGE}
                        style={{
                            lineHeight: "40px",
                            fontWeight: 600,
                            marginBottom: 20,
                        }}
                    >
                        Filter
                    </div>
                    <Button
                        style={{ position: "absolute", top: 20, right: 20 }}
                        icon={<FAIcon icon={faArrowLeft} />}
                        size={Size.LARGE}
                        variant={ButtonVariant.MINIMAL}
                        onClick={() => setShowFilter(false)}
                    />
                    <RadioGroup
                        selectedValue={filter.group}
                        label="Group"
                        style={{ marginTop: 20 }}
                    >
                        <Radio size={Size.LARGE} label="All" value="all" />
                        <Radio size={Size.LARGE} label="My" value="owner" />
                        <Radio
                            size={Size.LARGE}
                            label="Shared"
                            value="member"
                        />
                    </RadioGroup>
                </motion.div>
                <AutoSizer>
                    {({ width, height }) => (
                        <VariableSizeList
                            width={width}
                            height={height}
                            itemCount={_.size(allSessions)}
                            ref={variableSizeListRef}
                            itemSize={(index) => getRowHeight(index, width)}
                        >
                            {({ index, style }) => {
                                const last = _.isEqual(
                                    _.size(allSessions),
                                    index + 1
                                );
                                return (
                                    <div
                                        style={{
                                            ...style,
                                            paddingBottom: 10 + (last ? 10 : 0),
                                            paddingLeft: 20,
                                            paddingRight: 20,
                                        }}
                                    >
                                        {index > 0 ? (
                                            <SessionRow
                                                sessionId={allSessions[index]}
                                            />
                                        ) : (
                                            <ControlGroup
                                                style={{ marginTop: 20 }}
                                            >
                                                <Button
                                                    onClick={() =>
                                                        setShowFilter(true)
                                                    }
                                                    size={Size.LARGE}
                                                    icon={
                                                        <FAIcon
                                                            icon={faBarsFilter}
                                                        />
                                                    }
                                                    variant={
                                                        ButtonVariant.OUTLINED
                                                    }
                                                    intent={Intent.PRIMARY}
                                                    text="Filter"
                                                />
                                                <InputGroup
                                                    leftIcon={
                                                        <FAIcon
                                                            icon={faSearch}
                                                        />
                                                    }
                                                    size={Size.LARGE}
                                                />
                                            </ControlGroup>
                                        )}
                                    </div>
                                );
                            }}
                        </VariableSizeList>
                    )}
                </AutoSizer>
            </div>
        </div>
    );
}
export default withAutoSizer(SessionList);

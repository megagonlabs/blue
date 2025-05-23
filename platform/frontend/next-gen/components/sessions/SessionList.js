import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";
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
import { useEffect, useMemo, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import SessionCard from "./SessionCard";
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
    const user = useAuthStore((state) => state.user);
    const darkMode = useAppStore((state) => state.dark_mode);
    const { sessionIds, getSessions, sessions, filter } = useSessionStore(
        useShallow((state) => ({
            sessionIds: state.sessionIds,
            getSessions: state.getSessions,
            sessions: state.sessions,
            filter: state.filter,
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
                if (_.includes(id, filter.keywords)) {
                    return true;
                }
                const name = _.get(sessions, [id, "details", "name"], id);
                if (_.includes(name, filter.keywords)) {
                    return true;
                }
                const description = _.get(
                    sessions,
                    [id, "details", "description"],
                    id
                );
                if (_.includes(description, filter.keywords)) {
                    return true;
                }
                return false;
            })
            .sort((left, right) => {
                const leftPinned = _.get(
                    sessions,
                    [left, "details", "pinned", user.uid],
                    false
                );
                const rightPinned = _.get(
                    sessions,
                    [right, "details", "pinned", user.uid],
                    false
                );
                return _.isEqual(leftPinned, rightPinned)
                    ? _.get(sessions, [right, "details", "created_date"]) -
                          _.get(sessions, [left, "details", "created_date"])
                    : rightPinned - leftPinned;
            });
        return result;
    }, [sessionIds, filter, sessions]);
    const [showFilter, setShowFilter] = useState(false);
    useEffect(() => {
        getSessions();
    }, []);
    return (
        <div
            style={{
                width,
                height,
                backgroundColor: darkMode ? Colors.BLACK : null,
            }}
        >
            <div
                className="full-parent-dimension"
                style={{
                    padding: 20,
                    position: "relative",
                    overflowY: "auto",
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
                        onClick={() => {
                            setShowFilter(false);
                        }}
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
                <ControlGroup>
                    <Button
                        onClick={() => {
                            setShowFilter(true);
                        }}
                        size={Size.LARGE}
                        icon={<FAIcon icon={faBarsFilter} />}
                        variant={ButtonVariant.OUTLINED}
                        intent={Intent.PRIMARY}
                        text="Filter"
                    />
                    <InputGroup
                        leftIcon={<FAIcon icon={faSearch} />}
                        size={Size.LARGE}
                    />
                </ControlGroup>
                <div
                    style={{ marginTop: 20 }}
                    className="responsive-grid-container"
                >
                    {allSessions.map((session, index) => (
                        <div key={index} className="grid-item">
                            <SessionCard sessionId={session} />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(SessionList);

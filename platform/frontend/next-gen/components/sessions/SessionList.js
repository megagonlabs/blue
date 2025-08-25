import { useAppStore } from "@/stores/app-store";
import { useAuthStore } from "@/stores/auth-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    ButtonVariant,
    Colors,
    ControlGroup,
    InputGroup,
    Intent,
    Radio,
    RadioGroup,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import { faSearch } from "@fortawesome/pro-solid-svg-icons";
import {
    faArrowLeft,
    faBarsFilter,
    faEraser,
    faInboxArrowUp,
    faRefresh,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useEffect, useMemo, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import {
    HEX_TRANSPARENCY,
    POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10,
} from "../constants";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import FilterPane from "../registries/FilterPane";
import { CardListCallout } from "../ux/CardListCallout";
import SessionCard from "./SessionCard";
function SessionList({ width, height }) {
    const { user, permissions } = useAuthStore(
        useShallow((state) => ({
            user: state.user,
            permissions: state.permissions,
            logout: state.logout,
        }))
    );
    const darkMode = useAppStore((state) => state.dark_mode);
    const { sessionIds, getSessions, sessions, filter, setFilterValue } =
        useSessionStore(
            useShallow((state) => ({
                sessionIds: state.sessionIds,
                getSessions: state.getSessions,
                sessions: state.sessions,
                filter: state.filter,
                setFilterValue: state.setFilterValue,
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
                return _.isEqual(filter.group, "all") || group;
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
    }, [sessionIds, filter, sessions, user]);
    const [showFilter, setShowFilter] = useState(false);
    useEffect(() => {
        getSessions();
    }, [getSessions, filter.group]);
    const createNewSession = useSessionStore((state) => state.createNewSession);
    const elementRef = useRef(null);
    return (
        <div
            ref={elementRef}
            style={{
                width,
                height,
                backgroundColor: darkMode ? Colors.BLACK : null,
            }}
        >
            {showFilter && (
                <div
                    className="full-parent-dimension"
                    onClick={() => {
                        setShowFilter(false);
                    }}
                    style={{
                        position: "absolute",
                        zIndex: 1,
                        maxHeight: "calc(100% - 45px)",
                        backgroundColor: `${Colors.BLACK}${HEX_TRANSPARENCY[70]}`,
                    }}
                />
            )}
            <div
                className="full-parent-dimension"
                style={{
                    padding: 20,
                    position: "relative",
                    overflowY: "auto",
                }}
            >
                <FilterPane
                    showFilter={showFilter}
                    setShowFilter={setShowFilter}
                >
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
                        onChange={(event) => {
                            setFilterValue({
                                key: "group",
                                value: event.currentTarget.value,
                            });
                        }}
                    >
                        <Radio size={Size.LARGE} label="All" value="all" />
                        <Radio size={Size.LARGE} label="My" value="owner" />
                        <Radio
                            size={Size.LARGE}
                            label="Shared"
                            value="member"
                        />
                    </RadioGroup>
                </FilterPane>
                <ControlGroup>
                    <Button
                        size={Size.LARGE}
                        icon={<FAIcon icon={faRefresh} />}
                        variant={ButtonVariant.MINIMAL}
                        onClick={getSessions}
                    />
                    <Button
                        onClick={() => {
                            setShowFilter(true);
                        }}
                        size={Size.LARGE}
                        icon={<FAIcon icon={faBarsFilter} />}
                        variant={ButtonVariant.OUTLINED}
                        intent={Intent.PRIMARY}
                    />
                    <div style={{ width: 257, maxWidth: "calc(100% - 84px)" }}>
                        <InputGroup
                            leftIcon={<FAIcon icon={faSearch} />}
                            size={Size.LARGE}
                            rightElement={
                                !_.isEmpty(_.get(filter, "keywords", "")) && (
                                    <Tooltip
                                        {...POPPER_BOTTOM_WITH_MODIFIER_OVERFLOW_10}
                                        content="Clear search"
                                        boundary={elementRef.current}
                                    >
                                        <Button
                                            onClick={() => {
                                                setFilterValue({
                                                    key: "keywords",
                                                    value: "",
                                                });
                                            }}
                                            variant={ButtonVariant.MINIMAL}
                                            icon={<FAIcon icon={faEraser} />}
                                        />
                                    </Tooltip>
                                )
                            }
                            value={_.get(filter, "keywords", "")}
                            onValueChange={(value) => {
                                setFilterValue({ key: "keywords", value });
                            }}
                        />
                    </div>
                </ControlGroup>
                <div style={{ marginTop: 20 }}>
                    <CardListCallout />
                </div>
                <div
                    style={{ marginTop: 20 }}
                    className="responsive-grid-container"
                >
                    {allSessions.map((session, index) => (
                        <div key={index} className="grid-item">
                            <SessionCard sessionId={session} />
                        </div>
                    ))}
                    {permissions.canWriteSessions && (
                        <Button
                            className="session-list-new-session-button"
                            intent={Intent.PRIMARY}
                            onClick={() => {
                                createNewSession({});
                            }}
                            icon={<FAIcon icon={faInboxArrowUp} />}
                            size={Size.LARGE}
                            fill
                            variant={ButtonVariant.MINIMAL}
                            text="New session"
                        />
                    )}
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(SessionList);

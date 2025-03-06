import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import SearchResultRow from "@/components/sessions/SearchResultRow";
import {
    Button,
    Classes,
    ControlGroup,
    H4,
    H5,
    InputGroup,
    Intent,
    NonIdealState,
    Popover,
    Radio,
    RadioGroup,
} from "@blueprintjs/core";
import {
    faBarsFilter,
    faInboxes,
    faSearch,
    faTimes,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useMemo, useState } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList } from "react-window";
export default function AllSessions() {
    const { appState, appActions } = useContext(AppContext);
    const {
        sessionIds,
        sessionDetails,
        filter,
        pinnedSessionIds,
        sessionGroupBy,
    } = appState.session;
    const [loading, setLoading] = useState(false);
    const [keywords, setKeywords] = useState(filter.keywords);
    const allSessions = useMemo(() => {
        let result = sessionIds
            .filter((id) => {
                const groupByFlag = _.get(
                    appState,
                    `session.sessionDetails.${id}.group_by.${sessionGroupBy}`,
                    false
                );
                return _.isEqual(sessionGroupBy, "all") || groupByFlag;
            })
            .filter((id) => {
                if (_.includes(id, filter.keywords)) return true;
                const name = _.get(sessionDetails, [id, "name"], id);
                if (_.includes(name, filter.keywords)) return true;
                const description = _.get(
                    sessionDetails,
                    [id, "description"],
                    id
                );
                if (_.includes(description, filter.keywords)) return true;
                return false;
            })
            .sort((a, b) => {
                let aPinned = pinnedSessionIds.has(a),
                    bPinned = pinnedSessionIds.has(b);
                if (_.isEqual(aPinned, bPinned)) {
                    return (
                        sessionDetails[b].created_date -
                        sessionDetails[a].created_date
                    );
                } else {
                    return bPinned - aPinned;
                }
            });
        let insertedPinned = false;
        if (pinnedSessionIds.has(_.first(result))) {
            result.splice(0, 0, { header: "Pinned" });
            insertedPinned = true;
        }
        for (let i = 0 + (insertedPinned ? 1 : 0); i < _.size(result); i++) {
            if (!pinnedSessionIds.has(result[i])) {
                result.splice(i, 0, { header: "Everything else" });
                break;
            }
        }
        return result;
    }, [
        appState,
        sessionIds,
        pinnedSessionIds,
        sessionGroupBy,
        sessionDetails,
        filter.keywords,
    ]);
    useEffect(() => {
        // automatically fetch all existing sessions onload
        setLoading(true);
        // param: my_sessions, true/false
        const my_sessions = _.includes(["owner", "member"], sessionGroupBy);
        axios
            .get("/sessions", { params: { my_sessions } })
            .then((response) => {
                let sessions = _.get(response, "data.results", []);
                let members = new Set();
                appActions.session.setSessionDetails(sessions);
                for (let i = 0; i < _.size(sessions); i++) {
                    const sessionId = sessions[i].id;
                    const owner = sessions[i].created_by;
                    members.add(owner);
                    const sessionMembers = _.keys(sessions[i].members);
                    for (let j = 0; j < _.size(sessionMembers); j++) {
                        const isMember = _.get(
                            sessions,
                            [i, "members", sessionMembers[j]],
                            false
                        );
                        if (isMember) {
                            members.add(sessionMembers[j]);
                        }
                    }
                    appActions.session.addSession(sessionId);
                }
                members = _.toArray(members);
                for (let i = 0; i < _.size(members); i++) {
                    const uid = members[i];
                    const hasUserProfile = _.has(appState, [
                        "app",
                        "users",
                        uid,
                    ]);
                    if (!hasUserProfile) {
                        let pendingRquest = _.get(
                            appState,
                            ["app", "pendingRequests", `getUserProfile ${uid}`],
                            false
                        );
                        if (!pendingRquest) {
                            appActions.app.getUserProfile(uid);
                        }
                    }
                }
                setLoading(false);
            })
            .catch(() => {});
    }, [sessionGroupBy]); // eslint-disable-line react-hooks/exhaustive-deps
    return (
        <div className="full-parent-height">
            <div style={{ padding: "20px 20px 10px 20px", display: "flex" }}>
                <H4 style={{ margin: "0px 10px 0px 0px" }}>Sessions</H4>
            </div>
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    width: "100%",
                    padding: "0px 20px 10px 20px",
                }}
            >
                <div
                    style={{
                        maxWidth: 690,
                        width: "calc(100% - 250px - 40px)",
                    }}
                >
                    <ControlGroup fill>
                        <InputGroup
                            value={keywords}
                            className={loading ? Classes.SKELETON : null}
                            id="all-sessions-search-input"
                            placeholder="Search sessions"
                            size="large"
                            fill
                            onChange={(event) =>
                                setKeywords(event.target.value)
                            }
                            leftIcon={faIcon({ icon: faSearch })}
                            onKeyDown={(event) => {
                                if (_.isEqual(event.key, "Enter")) {
                                    appActions.session.setState({
                                        key: "filter",
                                        value: { keywords },
                                    });
                                }
                            }}
                            rightElement={
                                !_.isEmpty(filter.keywords) && (
                                    <Button
                                        variant="minimal"
                                        onClick={() => {
                                            setKeywords("");
                                            appActions.session.setState({
                                                key: "filter",
                                                value: { keywords: "" },
                                            });
                                        }}
                                        icon={faIcon({ icon: faTimes })}
                                    />
                                )
                            }
                        />
                        <Popover
                            minimal
                            placement="bottom-end"
                            content={
                                <div
                                    style={{
                                        padding: "15px 15px 5px",
                                        maxWidth: 500,
                                    }}
                                >
                                    <RadioGroup
                                        inline
                                        label="Type"
                                        selectedValue={sessionGroupBy}
                                        onChange={(event) =>
                                            appActions.session.setState({
                                                key: "sessionGroupBy",
                                                value: event.target.value,
                                            })
                                        }
                                    >
                                        {[
                                            { value: "all", text: "All" },
                                            { value: "owner", text: "My" },
                                            {
                                                value: "member",
                                                text: "Shared",
                                            },
                                        ].map(({ value, text }, index) => (
                                            <Radio
                                                className={
                                                    loading
                                                        ? Classes.SKELETON
                                                        : null
                                                }
                                                key={index}
                                                size="large"
                                                value={value}
                                                label={text}
                                            />
                                        ))}
                                    </RadioGroup>
                                </div>
                            }
                        >
                            <Button
                                intent={Intent.PRIMARY}
                                variant="outlined"
                                size="large"
                                text="Filter"
                                endIcon={faIcon({ icon: faBarsFilter })}
                            />
                        </Popover>
                    </ControlGroup>
                </div>
            </div>
            <div style={{ height: "calc(100% - 101px)" }}>
                <H4 style={{ margin: "0px 0px 10px 20px" }}>
                    {filter.keywords ? "Search Results" : "Contents"}
                </H4>
                <div
                    style={{
                        height: "calc(100% - 31px)",
                        overflowY: "auto",
                    }}
                >
                    {_.isEmpty(allSessions) ? (
                        <div
                            style={{ padding: "0px 20px 20px", height: "100%" }}
                        >
                            <NonIdealState
                                className={loading ? Classes.SKELETON : null}
                                icon={faIcon({ icon: faInboxes, size: 50 })}
                                title={`No Session`}
                            />
                        </div>
                    ) : (
                        <AutoSizer>
                            {({ width, height }) => (
                                <FixedSizeList
                                    style={{ paddingBottom: 10 }}
                                    width={width}
                                    height={height}
                                    itemCount={_.size(allSessions)}
                                    itemSize={69}
                                >
                                    {({ index, style }) => {
                                        const element = allSessions[index];
                                        return _.has(element, "header") ? (
                                            <div style={style}>
                                                <H5
                                                    style={{
                                                        margin: "31px 21px 0px",
                                                    }}
                                                >
                                                    {element.header}
                                                </H5>
                                            </div>
                                        ) : (
                                            <SearchResultRow
                                                style={style}
                                                sessionId={element}
                                            />
                                        );
                                    }}
                                </FixedSizeList>
                            )}
                        </AutoSizer>
                    )}
                </div>
            </div>
        </div>
    );
}

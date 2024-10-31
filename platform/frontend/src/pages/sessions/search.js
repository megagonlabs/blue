import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import SearchResultRow from "@/components/sessions/SearchResultRow";
import {
    Button,
    Classes,
    ControlGroup,
    H4,
    InputGroup,
    NonIdealState,
} from "@blueprintjs/core";
import {
    faInboxes,
    faSearch,
    faTimes,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList } from "react-window";
export default function AllSessions() {
    const { appState, appActions } = useContext(AppContext);
    const { sessionIds, sessionDetails, filter } = appState.session;
    const [loading, setLoading] = useState(false);
    const [allSessions, setAllSessions] = useState([]);
    const [keywords, setKeywords] = useState(filter.keywords);
    const [search, setSearch] = useState(false);
    const searchSessions = (searchTerm) => {
        appActions.session.setState({
            key: "filter",
            value: { keywords: searchTerm },
        });
        setAllSessions(
            sessionIds
                .filter((id) => {
                    if (_.includes(id, searchTerm)) return true;
                    const name = _.get(sessionDetails, [id, "name"], id);
                    if (_.includes(name, searchTerm)) return true;
                    const description = _.get(
                        sessionDetails,
                        [id, "description"],
                        id
                    );
                    if (_.includes(description, searchTerm)) return true;
                    return false;
                })
                .sort(
                    (a, b) =>
                        sessionDetails[b].created_date -
                        sessionDetails[a].created_date
                )
        );
        setSearch(!_.isEmpty(searchTerm));
    };
    useEffect(() => {
        searchSessions(keywords);
    }, [sessionIds]);
    useEffect(() => {
        // automatically fetch all existing sessions onload
        setLoading(true);
        axios
            .get("/sessions")
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
    }, []);
    return (
        <>
            <div style={{ padding: "20px 20px 10px 20px", display: "flex" }}>
                <H4 style={{ margin: "0px 10px 0px 0px" }}>All Sessions</H4>
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
                            large
                            fill
                            onChange={(event) =>
                                setKeywords(event.target.value)
                            }
                            leftIcon={faIcon({ icon: faSearch })}
                            onKeyDown={(event) => {
                                if (_.isEqual(event.key, "Enter")) {
                                    searchSessions(event.target.value);
                                }
                            }}
                            rightElement={
                                !_.isEmpty(keywords) || search ? (
                                    <Button
                                        minimal
                                        onClick={() => {
                                            setKeywords("");
                                            setSearch(false);
                                            searchSessions("");
                                        }}
                                        icon={faIcon({ icon: faTimes })}
                                    />
                                ) : null
                            }
                        />
                    </ControlGroup>
                </div>
            </div>
            <div style={{ height: "calc(100% - 101px)" }}>
                <H4 style={{ margin: "0px 0px 10px 20px" }}>
                    {search ? "Search Results" : "Contents"}
                </H4>
                <div
                    style={{
                        height: "calc(100% - 31px)",
                        overflowY: "auto",
                    }}
                >
                    {_.isEmpty(allSessions) ? (
                        <NonIdealState
                            className={loading ? Classes.SKELETON : null}
                            icon={faIcon({ icon: faInboxes, size: 50 })}
                            title={`No Session`}
                        />
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
                                    {({ index, style }) => (
                                        <SearchResultRow
                                            style={style}
                                            sessionId={allSessions[index]}
                                        />
                                    )}
                                </FixedSizeList>
                            )}
                        </AutoSizer>
                    )}
                </div>
            </div>
        </>
    );
}

import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import SearchResultRow from "@/components/sessions/SearchResultRow";
import { ControlGroup, H4, InputGroup } from "@blueprintjs/core";
import { faSearch } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList } from "react-window";
export default function AllSessions() {
    const { appState, appActions } = useContext(AppContext);
    const { sessionIds, sessionDetails, search } = appState.session;
    const [loading, setLoading] = useState(false);
    const [allSessions, setAllSessions] = useState([]);
    const fetchAllSessions = () => {
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
    };
    useEffect(() => {
        setAllSessions(
            sessionIds.sort(
                (a, b) =>
                    sessionDetails[b].created_date -
                    sessionDetails[a].created_date
            )
        );
    }, [sessionIds]);
    useEffect(() => {
        // automatically fetch all existing sessions onload
        fetchAllSessions();
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
                            id="all-sessions-search-input"
                            placeholder="Search sessions"
                            large
                            fill
                            leftIcon={faIcon({ icon: faSearch })}
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
                </div>
            </div>
        </>
    );
}

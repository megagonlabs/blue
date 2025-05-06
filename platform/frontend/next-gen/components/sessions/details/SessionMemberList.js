import { FAIcon } from "@/components/FAIcon";
import { showAxiosErrorToast } from "@/components/helper";
import NoResultsFound from "@/components/nonidealstates/NoResultsFound";
import { useAppStore } from "@/stores/app-store";
import { useDedupStore } from "@/stores/dedup-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    ButtonVariant,
    Card,
    CardList,
    Classes,
    Colors,
    InputGroup,
    Intent,
    Popover,
    Size,
    Tag,
} from "@blueprintjs/core";
import {
    faCircleCheck,
    faSearch,
    faTrash,
    faUserPlus,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _, { debounce } from "lodash";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import UserAvatar from "../UserAvatar";
export default function SessionMemberList({ sessionId }) {
    const { sessions, setSessionDetails } = useSessionStore(
        useShallow((state) => ({
            sessions: state.sessions,
            setSessionDetails: state.setSessionDetails,
        }))
    );
    const darkMode = useAppStore((state) => state.darkMode);
    const details = _.get(sessions, [sessionId, "details"], {});
    const owner = details.created_by;
    const members = useMemo(() => {
        return _.entries(_.get(details, "members", {}))
            .filter((user) => user[1] && !_.isEqual(user[0], owner))
            .map((user) => user[0]);
    }, [sessionId, details]);
    const { getUserProfile, addUserProfile, users } = useDedupStore(
        useShallow((state) => ({
            getUserProfile: state.getUserProfile,
            addUserProfile: state.addUserProfile,
            users: state.users,
        }))
    );

    const [searchKeyword, setSearchKeyword] = useState("");
    useEffect(() => {
        getUserProfile(owner);
        for (let i = 0; i < _.size(members); i++) {
            getUserProfile(members[i]);
        }
    }, [members]);
    const [showSearch, setShowSearch] = useState(false);
    const [searchResult, setSearchResult] = useState([]);
    const getSearchResult = useCallback((keyword) => {
        const query = _.trim(keyword);
        if (_.isEmpty(query)) {
            setSearchResult([]);
            return;
        }
        axios
            .get("/accounts/users", { params: { keyword } })
            .then((response) => {
                const users = _.get(response, "data.users", []);
                for (let i = 0; i < _.size(users); i++) {
                    addUserProfile(users[i]);
                }
                setSearchResult(users);
            });
    }, []);
    const debounced = useCallback(
        debounce(getSearchResult, 800),
        [getSearchResult] // Dependency on fetchSearchResults
    );
    const handleKeywordChange = (value) => {
        setSearchKeyword(value);
        debounced(value);
    };
    const updateSessionMember = (userId, operation) => {
        axios[operation](`/sessions/session/${sessionId}/members/${userId}`)
            .then(() => {
                setSessionDetails({
                    sessionId,
                    fields: [
                        {
                            path: ["members", userId],
                            value: _.isEqual(operation, "post"),
                        },
                    ],
                });
            })
            .catch((error) => {
                showAxiosErrorToast(error);
            });
    };
    useEffect(() => {
        axios.get(`/sessions/session/${sessionId}/members`).then((response) => {
            const results = _.get(response, "data.results", []);
            let fields = [];
            for (let i = 0; i < _.size(results); i++) {
                if (!results[i].owner) {
                    fields.push({
                        path: ["members", results[i].uid],
                        value: true,
                    });
                }
            }
            setSessionDetails({ sessionId, fields });
        });
    }, []);
    const elementRef = useRef(null);
    const popoverBoundary =
        elementRef.current &&
        elementRef.current.closest(".grid-container-boundary");
    return (
        <div
            ref={elementRef}
            className="full-parent-dimension"
            style={{ padding: 20, overflowY: "auto" }}
        >
            <Popover
                modifiers={{
                    offset: { enabled: true, options: { offset: [0, 10] } },
                }}
                autoFocus={false}
                enforceFocus={false}
                minimal
                onInteraction={(state) => {
                    setShowSearch(state);
                }}
                boundary={popoverBoundary}
                className="full-parent-width"
                matchTargetWidth
                isOpen={showSearch}
                content={
                    <div
                        style={{
                            borderRadius: 2,
                            padding: 10,
                            backgroundColor: darkMode
                                ? Colors.DARK_GRAY2
                                : null,
                        }}
                    >
                        {_.isEmpty(searchResult) ? (
                            <div style={{ padding: 10 }}>
                                <NoResultsFound />
                            </div>
                        ) : (
                            <CardList bordered={false}>
                                {searchResult.map((user) => (
                                    <Card
                                        interactive
                                        style={{ position: "relative" }}
                                    >
                                        <UserAvatar userId={user.uid} />
                                        <div
                                            style={{
                                                height: 40,
                                                marginLeft: 10,
                                                display: "flex",
                                                flexDirection: "column",
                                                justifyContent: "space-between",
                                            }}
                                        >
                                            <div>{user.name}</div>
                                            <div className={Classes.TEXT_MUTED}>
                                                {user.email}
                                            </div>
                                        </div>
                                        <div
                                            style={{
                                                position: "absolute",
                                                right: 20,
                                            }}
                                        >
                                            {_.includes(members, user.uid) ||
                                            _.isEqual(owner, user.uid) ? (
                                                <FAIcon
                                                    icon={faCircleCheck}
                                                    style={{
                                                        color: Colors.GREEN3,
                                                    }}
                                                />
                                            ) : (
                                                <Button
                                                    size={Size.LARGE}
                                                    intent={Intent.PRIMARY}
                                                    onClick={() =>
                                                        updateSessionMember(
                                                            user.uid,
                                                            "post"
                                                        )
                                                    }
                                                    icon={
                                                        <FAIcon
                                                            icon={faUserPlus}
                                                        />
                                                    }
                                                    variant={
                                                        ButtonVariant.OUTLINED
                                                    }
                                                    text="Add"
                                                />
                                            )}
                                        </div>
                                    </Card>
                                ))}
                            </CardList>
                        )}
                    </div>
                }
            >
                <InputGroup
                    value={searchKeyword}
                    onClick={(event) => {
                        if (showSearch) {
                            event.stopPropagation();
                        }
                    }}
                    onValueChange={handleKeywordChange}
                    leftIcon={<FAIcon icon={faSearch} />}
                    size={Size.LARGE}
                />
            </Popover>
            <CardList bordered={false} style={{ marginTop: 10 }}>
                <Card interactive style={{ position: "relative" }}>
                    <UserAvatar userId={owner} />
                    <div
                        style={{
                            height: 40,
                            marginLeft: 10,
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "space-between",
                        }}
                    >
                        <div>{_.get(users, [owner, "name"], "-")}</div>
                        <div className={Classes.TEXT_MUTED}>
                            {_.get(users, [owner, "email"], "-")}
                        </div>
                    </div>
                    <Tag
                        style={{ position: "absolute", right: 20 }}
                        size={Size.LARGE}
                        minimal
                        intent={Intent.PRIMARY}
                    >
                        Owner
                    </Tag>
                </Card>
                {members.map((member) => (
                    <Card interactive style={{ position: "relative" }}>
                        <UserAvatar userId={member} />
                        <div
                            style={{
                                height: 40,
                                marginLeft: 10,
                                display: "flex",
                                flexDirection: "column",
                                justifyContent: "space-between",
                            }}
                        >
                            <div>{_.get(users, [member, "name"], "-")}</div>
                            <div className={Classes.TEXT_MUTED}>
                                {_.get(users, [member, "email"], "-")}
                            </div>
                        </div>
                        <Button
                            style={{ position: "absolute", right: 20 }}
                            intent={Intent.DANGER}
                            size={Size.LARGE}
                            onClick={() =>
                                updateSessionMember(member, "delete")
                            }
                            icon={<FAIcon icon={faTrash} />}
                            variant={ButtonVariant.MINIMAL}
                        />
                    </Card>
                ))}
            </CardList>
        </div>
    );
}

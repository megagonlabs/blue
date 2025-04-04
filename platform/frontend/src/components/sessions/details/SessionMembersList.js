import { PROFILE_PICTURE_40 } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    Card,
    Classes,
    DialogBody,
    Icon,
    InputGroup,
    Intent,
    Popover,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faCircleCheck,
    faQuestion,
    faSearch,
    faTrash,
    faUserPlus,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import Image from "next/image";
import { useContext, useEffect, useMemo, useState } from "react";
const UserAvatar = ({ user, loading = false }) => {
    const picture = _.get(user, "picture", "");
    return (
        <Card
            style={PROFILE_PICTURE_40}
            className={loading ? Classes.SKELETON : null}
        >
            {_.isEmpty(picture) ? (
                <Icon icon={faIcon({ icon: faQuestion, size: 20 })} />
            ) : (
                <Image alt="" src={picture} width={40} height={40} />
            )}
        </Card>
    );
};
const UserInfo = ({ user, loading = false }) => (
    <div className={loading ? Classes.SKELETON : null}>
        <div style={{ fontWeight: 600 }}>{_.get(user, "name", "-")}</div>
        <div className={classNames(Classes.TEXT_DISABLED, Classes.TEXT_SMALL)}>
            {_.get(user, "email", "-")}
        </div>
    </div>
);
export default function SessionMembersList({ loading, setLoading }) {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [members, setMembers] = useState([]);
    const [keyword, setKeyword] = useState("");
    const [isSearchPopoverOpen, setIsSearchPopoverOpen] = useState(false);
    const [searchResult, setSearchResult] = useState([]);
    const [isTyping, setIsTyping] = useState(false);
    const [recentlyAdded, setRecentlyAdded] = useState(new Set());
    const memberIds = new Set(members.map((member) => member.uid));
    const fetchMemberList = () => {
        setLoading(true);
        axios
            .get(`/sessions/session/${sessionIdFocus}/members`)
            .then((response) => {
                const results = _.get(response, "data.results", []);
                let sessionDetailMembers = {};
                for (let i = 0; i < _.size(results); i++) {
                    const result = results[i];
                    if (!result.owner) {
                        sessionDetailMembers[result.uid] = true;
                    }
                    const hasUserProfile = _.has(appState, [
                        "app",
                        "users",
                        result.uid,
                    ]);
                    if (!hasUserProfile) {
                        let pendingRquest = _.get(
                            appState,
                            [
                                "app",
                                "pendingRequests",
                                `getUserProfile ${result.uid}`,
                            ],
                            false
                        );
                        if (!pendingRquest) {
                            appActions.app.getUserProfile(result.uid);
                        }
                    }
                }
                appActions.session.setSessionDetailMembers({
                    id: sessionIdFocus,
                    members: sessionDetailMembers,
                });
                setMembers(results);
                setLoading(false);
            });
    };
    useEffect(() => {
        fetchMemberList();
    }, []); // eslint-disable-line react-hooks/exhaustive-deps
    const handleSearchQuery = useMemo(
        () =>
            _.debounce((keyword) => {
                if (!_.isEmpty(keyword)) {
                    axios
                        .get("/accounts/users", {
                            params: { keyword: keyword },
                        })
                        .then((response) => {
                            setSearchResult(_.get(response, "data.users", []));
                        })
                        .finally(() => setIsTyping(false));
                } else {
                    setSearchResult([]);
                    setIsTyping(false);
                }
            }, 800),
        []
    );
    const LOADING_PLACEHOLDER = (
        <div
            style={{
                display: "flex",
                alignItems: "center",
                gap: 15,
                padding: "7.5px 15px",
                borderRadius: 2,
            }}
        >
            <Card
                className={Classes.SKELETON}
                style={{
                    borderRadius: "50%",
                    padding: 0,
                    overflow: "hidden",
                    width: 40,
                    height: 40,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                }}
            />
            <div className={Classes.SKELETON} style={{ width: 163.56 }}>
                &nbsp;
            </div>
        </div>
    );
    const removeMember = (user) => {
        const userName = _.get(user, "name", "-");
        axios
            .delete(`/sessions/session/${sessionIdFocus}/members/${user.uid}`)
            .then(() => {
                fetchMemberList();
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `Removed ${userName} from the session`,
                });
            });
    };
    const addMember = (user) => {
        axios
            .post(`/sessions/session/${sessionIdFocus}/members/${user.uid}`)
            .then(() => {
                let temp = _.cloneDeep(recentlyAdded);
                temp.add(user.uid);
                setRecentlyAdded(temp);
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `Added ${_.get(user, "name", "-")} to session`,
                });
            });
    };
    return (
        <DialogBody>
            <div
                style={{
                    minHeight: 202,
                    height: _.isEmpty(members) ? 202 : null,
                    maxHeight: 463,
                }}
            >
                <Popover
                    usePortal={false}
                    onInteraction={(state) => {
                        setIsSearchPopoverOpen(state);
                        if (!state && !_.isEmpty(recentlyAdded)) {
                            fetchMemberList();
                            setRecentlyAdded(new Set());
                        }
                    }}
                    matchTargetWidth
                    className="full-parent-width"
                    minimal
                    autoFocus={false}
                    enforceFocus={false}
                    modifiers={{
                        preventOverflow: { boundariesElement: "viewport" },
                    }}
                    isOpen={isSearchPopoverOpen}
                    placement="bottom-start"
                    content={
                        <div style={{ padding: 15 }}>
                            {_.isEmpty(searchResult) ? (
                                <div
                                    className={
                                        isTyping ? Classes.SKELETON : null
                                    }
                                >
                                    No results.
                                </div>
                            ) : null}
                            {searchResult.map((user) => {
                                return (
                                    <div
                                        key={user.uid}
                                        className="background-color-on-hover"
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 15,
                                            padding: "7.5px 15px",
                                            borderRadius: 2,
                                            position: "relative",
                                        }}
                                    >
                                        <UserAvatar
                                            user={user}
                                            loading={isTyping}
                                        />
                                        <UserInfo
                                            user={user}
                                            loading={isTyping}
                                        />
                                        {!recentlyAdded.has(user.uid) &&
                                        !memberIds.has(user.uid) ? (
                                            <Button
                                                intent={Intent.PRIMARY}
                                                variant="minimal"
                                                onClick={() => {
                                                    addMember(user);
                                                }}
                                                size="large"
                                                className={
                                                    isTyping
                                                        ? Classes.SKELETON
                                                        : null
                                                }
                                                style={{
                                                    position: "absolute",
                                                    right: 15,
                                                    top: 7.5,
                                                }}
                                                icon={faIcon({
                                                    icon: faUserPlus,
                                                })}
                                                text="Add"
                                            />
                                        ) : (
                                            faIcon({
                                                icon: faCircleCheck,
                                                size: 20,
                                                style: {
                                                    position: "absolute",
                                                    right: 39.387,
                                                    color: "#238551",
                                                },
                                            })
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    }
                >
                    <InputGroup
                        onClick={(event) => {
                            if (isSearchPopoverOpen) {
                                event.stopPropagation();
                            }
                        }}
                        autoFocus
                        leftIcon={faIcon({ icon: faSearch })}
                        placeholder="Search members"
                        size="large"
                        value={keyword}
                        onChange={(event) => {
                            setIsTyping(true);
                            setKeyword(event.target.value);
                            handleSearchQuery.call({}, event.target.value);
                        }}
                        style={{ marginBottom: 7.5 }}
                    />
                </Popover>
                {loading ? (
                    <>
                        {LOADING_PLACEHOLDER}
                        {LOADING_PLACEHOLDER}
                    </>
                ) : (
                    members.map((member) => {
                        const hasUserProfile = _.has(appState, [
                            "app",
                            "users",
                            member.uid,
                        ]);
                        if (!hasUserProfile) {
                            return (
                                <div key={member.uid}>
                                    {LOADING_PLACEHOLDER}
                                </div>
                            );
                        }
                        const user = _.get(
                            appState,
                            ["app", "users", member.uid],
                            {}
                        );
                        return (
                            <div
                                key={member.uid}
                                className="background-color-on-hover"
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 15,
                                    padding: "7.5px 15px",
                                    borderRadius: 2,
                                    position: "relative",
                                }}
                            >
                                <UserAvatar user={user} />
                                <UserInfo user={user} />
                                {member.owner ? (
                                    <Tag
                                        size="large"
                                        minimal
                                        intent={Intent.PRIMARY}
                                        style={{
                                            position: "absolute",
                                            right: 15,
                                            top: 12.5,
                                        }}
                                    >
                                        Owner
                                    </Tag>
                                ) : (
                                    <div
                                        style={{
                                            position: "absolute",
                                            right: 15,
                                            top: 7.5,
                                        }}
                                    >
                                        <Popover
                                            usePortal={false}
                                            placement="left"
                                            content={
                                                <div style={{ padding: 15 }}>
                                                    <Button
                                                        className={
                                                            Classes.POPOVER_DISMISS
                                                        }
                                                        size="large"
                                                        text="Confirm"
                                                        onClick={() => {
                                                            removeMember(user);
                                                        }}
                                                        intent={Intent.DANGER}
                                                    />
                                                </div>
                                            }
                                        >
                                            <Tooltip
                                                content="Remove"
                                                minimal
                                                placement="left"
                                            >
                                                <Button
                                                    size="large"
                                                    variant="minimal"
                                                    icon={faIcon({
                                                        icon: faTrash,
                                                    })}
                                                    intent={Intent.DANGER}
                                                />
                                            </Tooltip>
                                        </Popover>
                                    </div>
                                )}
                            </div>
                        );
                    })
                )}
                {!_.isEmpty(members) && <div style={{ height: 15 }}></div>}
            </div>
        </DialogBody>
    );
}

import { PROFILE_PICTURE_40 } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
import {
    Button,
    Card,
    Classes,
    DialogBody,
    InputGroup,
    Intent,
    Popover,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faCircleCheck,
    faSearch,
    faTrash,
    faUserPlus,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import Image from "next/image";
import { useCallback, useContext, useEffect, useState } from "react";
const UserAvatar = ({ user, loading = false }) => (
    <Card
        style={PROFILE_PICTURE_40}
        className={loading ? Classes.SKELETON : null}
    >
        <Image alt="" src={_.get(user, "picture", "")} width={40} height={40} />
    </Card>
);
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
                        appActions.app.getUserProfile(result.uid);
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
    }, []);
    const handleSearchQuery = useCallback(
        _.debounce((keyword) => {
            if (!_.isEmpty(keyword)) {
                axios
                    .get("/accounts/users", { params: { keyword: keyword } })
                    .then((response) => {
                        setSearchResult(_.get(response, "data.users", []));
                    })
                    .finally(() => {
                        setIsTyping(false);
                    });
            } else {
                setSearchResult([]);
                setIsTyping(false);
            }
        }, 800),
        [members]
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
        axios
            .delete(`/sessions/session/${sessionIdFocus}/members/${user.uid}`)
            .then(() => {
                fetchMemberList();
                AppToaster.show({
                    intent: Intent.SUCCESS,
                    message: `Removed ${_.get(
                        user,
                        "name",
                        "-"
                    )} from the session`,
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
        <DialogBody className="dialog-body">
            <div
                style={{
                    padding: 15,
                    minHeight: 202,
                    height: _.isEmpty(members) ? 202 : null,
                }}
            >
                <Popover
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
                        <div style={{ padding: 7.5 }}>
                            {_.isEmpty(searchResult) ? (
                                <div
                                    style={{ padding: 7.5 }}
                                    className={
                                        isTyping ? Classes.SKELETON : null
                                    }
                                >
                                    No result
                                </div>
                            ) : null}
                            {searchResult.map((user) => {
                                return (
                                    <div
                                        key={user.uid}
                                        className="on-hover-background-color-bp-gray-3"
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
                                                minimal
                                                onClick={() => {
                                                    addMember(user);
                                                }}
                                                className={
                                                    isTyping
                                                        ? Classes.SKELETON
                                                        : null
                                                }
                                                style={{
                                                    position: "absolute",
                                                    right: 15,
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
                        large
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
                                className="on-hover-background-color-bp-gray-3"
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
                                        minimal
                                        intent={Intent.PRIMARY}
                                        style={{
                                            position: "absolute",
                                            right: 15,
                                        }}
                                    >
                                        Owner
                                    </Tag>
                                ) : (
                                    <div
                                        style={{
                                            position: "absolute",
                                            right: 15,
                                        }}
                                    >
                                        <Popover
                                            placement="left"
                                            content={
                                                <div style={{ padding: 15 }}>
                                                    <Button
                                                        className={
                                                            Classes.POPOVER_DISMISS
                                                        }
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
                                                    minimal
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
            </div>
        </DialogBody>
    );
}

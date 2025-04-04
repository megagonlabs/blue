import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import {
    Button,
    Card,
    Checkbox,
    Classes,
    Dialog,
    DialogBody,
    DialogFooter,
    Intent,
    NonIdealState,
    Tag,
} from "@blueprintjs/core";
import {
    faCheck,
    faCircleA,
    faCircleCheck,
    faForward,
    faGrid2Plus,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { FixedSizeList } from "react-window";
import { ENTITY_ICON_40 } from "../constant";
import { AuthContext } from "../contexts/auth-context";
import EntityIcon from "../entity/EntityIcon";
import { axiosErrorToast } from "../helper";
export default function AddAgents({
    isOpen,
    setIsAddAgentsOpen,
    setSkippable,
    skippable = false,
}) {
    const { appState, appActions } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [loading, setLoading] = useState(true);
    const [agents, setAgents] = useState(null);
    const [unavailableAgents, setUnavailableAgents] = useState(null);
    const [selected, setSelected] = useState(new Set());
    const [added, setAdded] = useState(new Set());
    const { settings } = useContext(AuthContext);
    const darkMode = _.get(settings, "dark_mode", false);
    const selectionSize =
        _.size(selected) -
        _.size(_.intersection(Array.from(selected), Array.from(added)));
    const toggleSelectedAgent = (name) => {
        if (_.isEmpty(name)) return;
        let nextSelected = _.clone(selected);
        if (nextSelected.has(name)) {
            nextSelected.delete(name);
        } else {
            nextSelected.add(name);
        }
        setSelected(nextSelected);
    };
    useEffect(() => {
        if (!isOpen) {
            setSelected(new Set());
            setAdded(new Set());
            return;
        }
        setLoading(true);
        axios
            .get(`/registry/${appState.agent.registryName}/agents`, {
                params: { recursive: true },
            })
            .then((response) => {
                const list = _.get(response, "data.results", []);
                let options = [];
                let unavailable = [];
                for (let i = 0; i < _.size(list); i++) {
                    let containerStatus = _.get(
                        list,
                        [i, "container", "status"],
                        null
                    );
                    const displayName = _.get(
                        list,
                        [i, "properties", "display_name"],
                        list[i].name
                    );
                    const description = _.get(list, [i, "description"], "");
                    const option = {
                        displayName: _.toString(displayName),
                        description: description,
                        name: list[i].name,
                    };
                    if (!_.isEqual(containerStatus, "running")) {
                        unavailable.push(option);
                    } else {
                        options.push(option);
                        if (!_.has(appState, ["agent", "icon", list[i].name])) {
                            appActions.agent.fetchAttributes(list[i].name);
                        }
                    }
                }
                options.sort(function (a, b) {
                    return a.name.localeCompare(b.name);
                });
                unavailable.sort(function (a, b) {
                    return a.name.localeCompare(b.name);
                });
                setAgents(options);
                setUnavailableAgents(unavailable);
                setLoading(false);
            })
            .catch(() => {
                setLoading(false);
            });
    }, [isOpen]); // eslint-disable-line react-hooks/exhaustive-deps
    const handleAddAgents = () => {
        setLoading(true);
        let promises = [];
        const selectedAgents = Array.from(selected);
        for (let i = 0; i < _.size(selectedAgents); i++) {
            const agentName = selectedAgents[i];
            if (added.has(agentName)) {
                continue;
            }
            promises.push(
                new Promise((resolve, reject) => {
                    axios
                        .post(
                            `/sessions/session/${sessionIdFocus}/agent/${agentName}`,
                            { properties: {} }
                        )
                        .then(() => {
                            resolve(agentName);
                        })
                        .catch((error) => {
                            axiosErrorToast(error);
                            reject(agentName);
                        });
                })
            );
        }
        Promise.allSettled(promises).then((results) => {
            let newAdded = _.clone(added);
            for (let i = 0; i < _.size(results); i++) {
                if (!_.isEqual("fulfilled", results[i].status)) continue;
                newAdded.add(results[i].value);
            }
            setAdded(newAdded);
            setLoading(false);
        });
    };
    return (
        <Dialog
            className={darkMode ? Classes.DARK : null}
            portalClassName="portal-overlay-z-index-36"
            title="Add Agents"
            canOutsideClickClose={_.isEqual(selectionSize, 0)}
            isOpen={isOpen}
            onClose={() => {
                if (loading) return;
                setIsAddAgentsOpen(false);
                setSkippable(false);
            }}
        >
            <DialogBody className="margin-0" style={{ padding: 0 }}>
                {_.isEmpty(agents) ? (
                    <div style={{ height: 141 }}>
                        <NonIdealState
                            className={loading ? Classes.SKELETON : null}
                            title="No Agent"
                            icon={faIcon({ icon: faCircleA, size: 50 })}
                        />
                    </div>
                ) : (
                    <FixedSizeList
                        itemCount={_.size(agents)}
                        style={{ paddingBottom: 20, marginTop: 1 }}
                        itemSize={63.43}
                        height={350.58}
                    >
                        {({ index, style }) => {
                            const name = agents[index].name,
                                displayName = agents[index].displayName;
                            return (
                                <Card
                                    onClick={() => {
                                        if (loading) return;
                                        toggleSelectedAgent(name);
                                    }}
                                    style={{
                                        ...style,
                                        cursor: !added.has(name)
                                            ? "pointer"
                                            : null,
                                        padding: "7px 15px",
                                        display: "flex",
                                        height: 48.43,
                                        margin: 15,
                                        maxWidth: "calc(100% - 30px)",
                                        alignItems: "center",
                                    }}
                                >
                                    {added.has(name) ? (
                                        faIcon({
                                            icon: faCircleCheck,
                                            size: 20,
                                            style: {
                                                marginRight: 10,
                                                color: "#238551",
                                            },
                                        })
                                    ) : loading ? (
                                        <div
                                            className={Classes.SKELETON}
                                            style={{
                                                width: 20,
                                                height: 20,
                                                marginRight: 10,
                                            }}
                                        >
                                            &nbsp;
                                        </div>
                                    ) : (
                                        <Checkbox
                                            checked={selected.has(name)}
                                            size="large"
                                            className="margin-0"
                                        />
                                    )}
                                    <div
                                        className={
                                            loading &&
                                            _.isEqual(selectionSize, 0)
                                                ? Classes.SKELETON
                                                : null
                                        }
                                        style={{
                                            maxWidth: "calc(100% - 30px)",
                                        }}
                                    >
                                        <div
                                            style={{
                                                display: "flex",
                                                alignItems: "center",
                                            }}
                                        >
                                            <div style={ENTITY_ICON_40}>
                                                <EntityIcon
                                                    entity={{
                                                        type: "agent",
                                                        icon: _.get(appState, [
                                                            "agent",
                                                            "icon",
                                                            name,
                                                        ]),
                                                    }}
                                                />
                                            </div>
                                            <div
                                                style={{
                                                    marginLeft: 5,
                                                    maxWidth:
                                                        "calc(100% - 45px)",
                                                }}
                                            >
                                                {displayName}
                                                <div
                                                    className={classNames(
                                                        Classes.TEXT_MUTED,
                                                        Classes.TEXT_SMALL,
                                                        Classes.TEXT_OVERFLOW_ELLIPSIS
                                                    )}
                                                >
                                                    {_.get(
                                                        agents,
                                                        [index, "description"],
                                                        ""
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </Card>
                            );
                        }}
                    </FixedSizeList>
                )}
            </DialogBody>
            <DialogFooter className="position-relative">
                <div style={{ display: "flex", alignItems: "center" }}>
                    <Button
                        className={_.isNil(agents) ? Classes.SKELETON : null}
                        disabled={!skippable && _.isEqual(selectionSize, 0)}
                        intent={
                            skippable &&
                            _.isEqual(selectionSize, 0) &&
                            !_.isEmpty(added)
                                ? Intent.SUCCESS
                                : Intent.PRIMARY
                        }
                        loading={selectionSize > 0 && loading}
                        size="large"
                        icon={faIcon({
                            icon:
                                skippable && _.isEqual(selectionSize, 0)
                                    ? !_.isEmpty(added)
                                        ? faCheck
                                        : faForward
                                    : faGrid2Plus,
                        })}
                        text={
                            skippable && _.isEqual(selectionSize, 0)
                                ? !_.isEmpty(added)
                                    ? "Done"
                                    : "Skip"
                                : "Add"
                        }
                        onClick={() => {
                            if (skippable && _.isEqual(selectionSize, 0)) {
                                setIsAddAgentsOpen(false);
                                setSkippable(false);
                            } else {
                                handleAddAgents();
                            }
                        }}
                    />
                    {selectionSize > 0 ? (
                        <span style={{ marginLeft: 15 }}>
                            {selectionSize} selected
                        </span>
                    ) : null}
                </div>
                {!_.isEmpty(unavailableAgents) && (
                    <div style={{ position: "absolute", right: 15, top: 15 }}>
                        <Tag intent={Intent.WARNING} minimal size="large">
                            {_.size(unavailableAgents)} unavailable
                        </Tag>
                    </div>
                )}
            </DialogFooter>
        </Dialog>
    );
}

import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import { AppToaster } from "@/components/toaster";
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
} from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { FixedSizeList } from "react-window";
export default function AddAgents({
    isOpen,
    setIsAddAgentsOpen,
    setSkippable,
    skippable = false,
}) {
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const registryName = appState.agent.registryName;
    const [loading, setLoading] = useState(true);
    const [agents, setAgents] = useState(null);
    const [unavailableAgents, setUnavailableAgents] = useState(null);
    const [selected, setSelected] = useState(new Set());
    const [added, setAdded] = useState(new Set());
    const selectionSize =
        _.size(selected) -
        _.size(_.intersection(Array.from(selected), Array.from(added)));
    const toggleSelectedAgent = (name) => {
        if (_.isEmpty(name)) {
            return;
        }
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
            .get(`/registry/${registryName}/agents`)
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
                    if (!_.isEqual(containerStatus, "running")) {
                        unavailable.push({
                            name: _.get(list, [i, "name"], ""),
                            description: _.get(list, [i, "description"], ""),
                        });
                    } else {
                        options.push({
                            name: _.get(list, [i, "name"], ""),
                            description: _.get(list, [i, "description"], ""),
                        });
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
    }, [isOpen]);
    const handleAddAgents = () => {
        let promises = [];
        const selectedAgents = Array.from(selected);
        for (let i = 0; i < _.size(selectedAgents); i++) {
            const agentName = selectedAgents[i];
            if (added.has(agentName)) continue;
            promises.push(
                new Promise((resolve, reject) => {
                    axios
                        .post(
                            `/sessions/session/${sessionIdFocus}/agents/${registryName}/agent/${agentName}`,
                            { properties: {} }
                        )
                        .then(() => {
                            resolve(agentName);
                        })
                        .catch((error) => {
                            AppToaster.show({
                                intent: Intent.DANGER,
                                message: `${error.name}: ${error.message}`,
                            });
                            reject(agentName);
                        });
                })
            );
        }
        setLoading(true);
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
            title="Add Agents"
            canOutsideClickClose={_.isEqual(selectionSize, 0)}
            isOpen={isOpen}
            onClose={() => {
                if (loading) {
                    return;
                }
                setIsAddAgentsOpen(false);
                setSkippable(false);
            }}
        >
            <DialogBody className="padding-0">
                {_.isEmpty(agents) ? (
                    <div style={{ padding: 15 }}>
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
                        itemSize={58.43}
                        height={350.58}
                    >
                        {({ index, style }) => {
                            const name = _.get(agents, [index, "name"], "");
                            return (
                                <Card
                                    onClick={() => {
                                        if (loading) {
                                            return;
                                        }
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
                                            large
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
                                            marginLeft: 5,
                                            maxWidth: "calc(100% - 35px)",
                                        }}
                                    >
                                        {name}
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
                        large
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
                <div style={{ position: "absolute", right: 15, top: 15 }}>
                    <Tag intent={Intent.WARNING} minimal large>
                        {_.size(unavailableAgents)} unavailable
                    </Tag>
                </div>
            </DialogFooter>
        </Dialog>
    );
}

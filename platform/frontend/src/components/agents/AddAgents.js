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
} from "@blueprintjs/core";
import { faCircleA, faGrid2Plus } from "@fortawesome/pro-duotone-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useContext, useEffect, useState } from "react";
import { FixedSizeList } from "react-window";
import { AppContext } from "../contexts/app-context";
import { faIcon } from "../icon";
export default function AddAgents({
    isOpen,
    setIsAddAgentsOpen,
    skippable = false,
}) {
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [loading, setLoading] = useState(false);
    const [agents, setAgents] = useState([]);
    const [selected, setSelected] = useState(new Set());
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
            return;
        }
        setLoading(true);
        axios
            .get("/agents")
            .then((response) => {
                setLoading(false);
                const list = _.get(response, "data.results", []);
                let options = [];
                for (let i = 0; i < _.size(list); i++) {
                    options.push({
                        name: _.get(list, [i, "name"], ""),
                        description: _.get(list, [i, "description"], ""),
                    });
                }
                options.sort(function (a, b) {
                    return a.name.localeCompare(b.name);
                });
                setAgents(options);
            })
            .catch((error) => {
                setLoading(false);
            });
    }, [isOpen]);
    return (
        <Dialog
            title="Add Agents"
            canOutsideClickClose={false}
            isOpen={isOpen}
            onClose={() => {
                if (loading) return;
                setIsAddAgentsOpen(false);
            }}
        >
            <DialogBody className="padding-0">
                {_.isEmpty(agents) ? (
                    <div style={{ padding: "20px 15px" }}>
                        <NonIdealState
                            className={loading ? Classes.SKELETON : null}
                            title="No Agent"
                            icon={faIcon({ icon: faCircleA, size: 50 })}
                        />
                    </div>
                ) : (
                    <FixedSizeList
                        itemCount={_.size(agents)}
                        style={{ padding: "20px 15px 11px", marginTop: 1 }}
                        itemSize={58.43}
                        height={362}
                    >
                        {({ index, style }) => {
                            const name = _.get(agents, [index, "name"], "");
                            return (
                                <Card
                                    onClick={() => {
                                        toggleSelectedAgent(name);
                                    }}
                                    interactive
                                    className="on-hover-z-index-1"
                                    style={{
                                        ...style,
                                        padding: "7px 15px",
                                        display: "flex",
                                        height: 48.43,
                                        margin: "20px 15px",
                                        maxWidth: "calc(100% - 30px)",
                                        alignItems: "center",
                                    }}
                                >
                                    <Checkbox
                                        checked={selected.has(name)}
                                        large
                                        className="margin-0"
                                    />
                                    <div
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
            <DialogFooter>
                <Button
                    disabled={!skippable && _.isEmpty(selected)}
                    intent={Intent.PRIMARY}
                    large
                    icon={faIcon({ icon: faGrid2Plus })}
                    text="Add"
                />
            </DialogFooter>
        </Dialog>
    );
}

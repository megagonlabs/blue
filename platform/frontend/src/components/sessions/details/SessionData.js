import JsonEditor from "@/components/codemirror/JsonEditor";
import { AppContext } from "@/components/contexts/app-context";
import {
    constructSavePropertyRequests,
    settlePromises,
    shallowDiff,
} from "@/components/helper";
import { faIcon } from "@/components/icon";
import {
    Button,
    ButtonGroup,
    Classes,
    DialogBody,
    DialogFooter,
    Intent,
    NonIdealState,
    Popover,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faCheck,
    faFolderOpen,
    faPen,
    faXmarkLarge,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import { useContext, useEffect, useState } from "react";
import JsonViewer from "../message/renderers/JsonViewer";
export default function SessionData() {
    const { appState } = useContext(AppContext);
    const { sessionIdFocus } = appState.session;
    const [data, setData] = useState(null);
    const [editData, setEditData] = useState(null);
    const [edit, setEdit] = useState(false);
    const [loading, setLoading] = useState(false);
    const [jsonError, setJsonError] = useState(false);
    const discard = () => {
        setEdit(false);
        setEditData(data);
        setJsonError(false);
    };
    useEffect(() => {
        // fetch session data
        setLoading(true);
        axios
            .get(`/sessions/session/${sessionIdFocus}/data`)
            .then((response) => {
                const responseData = _.get(response, "data.result", {});
                setData(responseData);
                setEditData(responseData);
                setLoading(false);
            });
    }, []); // eslint-disable-line react-hooks/exhaustive-deps
    const saveData = () => {
        const urlPrefix = `/sessions/session/${sessionIdFocus}/data`;
        setLoading(true);
        const difference = shallowDiff(data, editData);
        const tasks = constructSavePropertyRequests({
            axios,
            url: urlPrefix,
            difference,
            properties: editData,
        });
        settlePromises(tasks, ({ error }) => {
            if (!error) {
                setEdit(false);
                setData(editData);
            }
            setLoading(false);
        });
    };
    return (
        <>
            <DialogBody style={{ margin: "1px 0px 0px 0px" }}>
                <div style={{ maxHeight: 463, minHeight: 141 }}>
                    {!edit ? (
                        _.isEmpty(data) ? (
                            <div style={{ height: 141 }}>
                                <NonIdealState
                                    title="No Data"
                                    icon={faIcon({
                                        icon: faFolderOpen,
                                        size: 50,
                                    })}
                                />
                            </div>
                        ) : (
                            <div onDoubleClick={() => setEdit(true)}>
                                <JsonViewer json={data} />
                            </div>
                        )
                    ) : (
                        <JsonEditor
                            code={JSON.stringify(editData, null, 4)}
                            setCode={(code) => {
                                setEditData(JSON.parse(code));
                            }}
                            setLoading={setLoading}
                            setError={setJsonError}
                        />
                    )}
                </div>
            </DialogBody>
            <DialogFooter className="position-relative">
                <ButtonGroup>
                    {edit && (
                        <Popover
                            usePortal={false}
                            placement="top-start"
                            content={
                                <div style={{ padding: 15 }}>
                                    <Button
                                        size="large"
                                        className={Classes.POPOVER_DISMISS}
                                        text="Confirm"
                                        onClick={discard}
                                        intent={Intent.DANGER}
                                    />
                                </div>
                            }
                        >
                            <Tooltip
                                usePortal={false}
                                minimal
                                placement="top-start"
                                content="Discard"
                            >
                                <Button
                                    size="large"
                                    variant="minimal"
                                    icon={faIcon({ icon: faXmarkLarge })}
                                />
                            </Tooltip>
                        </Popover>
                    )}
                    <Button
                        size="large"
                        className={loading ? Classes.SKELETON : null}
                        text={edit ? "Save" : "Edit"}
                        onClick={() => {
                            if (!edit) setEdit(true);
                            else saveData();
                        }}
                        disabled={jsonError}
                        intent={edit ? Intent.SUCCESS : Intent.PRIMARY}
                        icon={faIcon({ icon: edit ? faCheck : faPen })}
                    />
                </ButtonGroup>
                {jsonError && edit && (
                    <div style={{ position: "absolute", right: 15, top: 15 }}>
                        <Tag intent={Intent.DANGER} minimal size="large">
                            Invalid JSON
                        </Tag>
                    </div>
                )}
            </DialogFooter>
        </>
    );
}

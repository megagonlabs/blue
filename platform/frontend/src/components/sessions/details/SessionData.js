import JsonEditor from "@/components/codemirror/JsonEditor";
import { AppContext } from "@/components/contexts/app-context";
import {
    constructSavePropertyRequests,
    settlePromises,
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
import { diff } from "deep-diff";
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
    }, []);
    const saveData = () => {
        const urlPrefix = `/sessions/session/${sessionIdFocus}/data`;
        setLoading(true);
        const difference = diff(data, editData);
        const tasks = constructSavePropertyRequests({
            axios,
            url: urlPrefix,
            difference,
            properties: editData,
        });
        settlePromises(tasks, (error) => {
            if (!error) {
                setEdit(false);
                setData(editData);
            }
            setLoading(false);
        });
    };
    return (
        <>
            <DialogBody className="dialog-body">
                <div style={{ maxHeight: 463 }}>
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
                            <div
                                style={{ padding: 15 }}
                                onDoubleClick={() => setEdit(true)}
                            >
                                <JsonViewer displaySize={true} json={data} />
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
                <ButtonGroup large>
                    {edit && (
                        <Popover
                            placement="top-start"
                            content={
                                <div style={{ padding: 15 }}>
                                    <Button
                                        className={Classes.POPOVER_DISMISS}
                                        text="Confirm"
                                        onClick={discard}
                                        intent={Intent.DANGER}
                                    />
                                </div>
                            }
                        >
                            <Tooltip
                                minimal
                                placement="top-start"
                                content="Discard"
                            >
                                <Button
                                    minimal
                                    icon={faIcon({ icon: faXmarkLarge })}
                                />
                            </Tooltip>
                        </Popover>
                    )}
                    <Button
                        className={loading ? Classes.SKELETON : null}
                        text={edit ? "Save" : "Edit"}
                        onClick={() => {
                            if (!edit) setEdit(true);
                            else saveData();
                        }}
                        intent={edit ? Intent.SUCCESS : Intent.PRIMARY}
                        icon={faIcon({ icon: edit ? faCheck : faPen })}
                    />
                </ButtonGroup>
                {jsonError && edit && (
                    <div style={{ position: "absolute", right: 15, top: 15 }}>
                        <Tag intent={Intent.DANGER} minimal large>
                            Invalid JSON
                        </Tag>
                    </div>
                )}
            </DialogFooter>
        </>
    );
}

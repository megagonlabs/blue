import {
    HEX_TRANSPARENCY,
    MAIN_INFO_STYLES,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import { getUpdatePropertyPromises, settlePromises } from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import { Classes, Colors } from "@blueprintjs/core";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import shallowDiff from "shallow-diff";
import EntityActions from "../EntityActions";
import RegistryEntityIcon from "../RegistryEntityIcon";
import EntityDescription from "../attributes/EntityDescription";
import EntityProperties from "../attributes/EntityProperties";
const { NEXT_PUBLIC_AGENT_REGISTRY_NAME } = allEnv();
export default function OutputEntity({ entity }) {
    const { name, scope, type } = entity;
    const [output, setOutput] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedOutput, setEditedOutput] = useState(null);
    const [loading, setLoading] = useState(false);
    const updateOutput = ({ path, value }) => {
        let newOutput = _.cloneDeep(editedOutput);
        _.set(newOutput, path, value);
        setEditedOutput(newOutput);
    };
    const darkMode = useAppStore((state) => state.dark_mode);
    const path = [scope.substring(1), type, name]
        .filter((str) => !_.isEmpty(str))
        .join("/");
    const url = `/registry/${NEXT_PUBLIC_AGENT_REGISTRY_NAME}/${path}`;
    useEffect(() => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                setOutput(result);
                setEditedOutput(result);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [entity]);
    const handleDiscard = () => {
        setEditedOutput(output);
        setIsEditing(false);
    };
    const handleSave = () => {
        setLoading(true);
        axios
            .put(url, {
                name: editedOutput.name,
                description: editedOutput.description,
            })
            .then(() => {
                const properties = editedOutput.properties;
                const diffs = shallowDiff(output.properties, properties);
                const tasks = getUpdatePropertyPromises({
                    axios,
                    url: `${url}/property`,
                    diffs,
                    properties,
                });
                settlePromises(tasks, ({ error }) => {
                    if (!error) {
                        setOutput(editedOutput);
                        setIsEditing(false);
                    }
                    setLoading(false);
                });
            });
    };
    return (
        <div>
            <div
                style={{
                    backgroundColor: `${Colors.BLUE3}${
                        HEX_TRANSPARENCY[darkMode ? 20 : 10]
                    }`,
                    borderRadius: 2,
                    padding: 20,
                    position: "relative",
                }}
            >
                {!_.isEmpty(output) && (
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={{ position: "absolute", right: 20 }}
                    >
                        <EntityActions
                            loading={loading}
                            handleSave={handleSave}
                            handleDiscard={handleDiscard}
                            entity={output}
                            isEditing={isEditing}
                            setIsEditing={setIsEditing}
                        />
                    </div>
                )}
                <div
                    className={classNames(
                        "padding-0",
                        "overflow-hidden",
                        "custom-card",
                        { [Classes.SKELETON]: loading }
                    )}
                    style={{
                        ...REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
                        position: "absolute",
                        left: 20,
                        top: 20,
                    }}
                >
                    <RegistryEntityIcon
                        content={_.get(editedOutput, "icon", null)}
                    />
                </div>
                <div
                    style={{
                        display: "flex",
                        marginLeft: 60,
                        columnGap: 40,
                        rowGap: 20,
                        flexWrap: "wrap",
                        paddingRight: isEditing ? 150.96 : 60,
                    }}
                >
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={MAIN_INFO_STYLES}
                    >
                        <div>{_.get(editedOutput, "type")}</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(editedOutput, "name")}
                        </div>
                    </div>
                </div>
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityDescription
                    isEditing={isEditing}
                    updateEntity={updateOutput}
                    entity={editedOutput}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityProperties
                    isEditing={isEditing}
                    updateEntity={updateOutput}
                    entity={editedOutput}
                    loading={loading}
                />
            </div>
        </div>
    );
}

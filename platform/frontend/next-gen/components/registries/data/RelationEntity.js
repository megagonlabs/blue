import {
    HEX_TRANSPARENCY,
    MAIN_INFO_STYLES,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import { useAppStore } from "@/stores/app-store";
import { Classes, Colors } from "@blueprintjs/core";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import EntityDescription from "../attributes/EntityDescription";
import EntityProperties from "../attributes/EntityProperties";
import EntityActions from "../EntityActions";
import RegistryEntityIcon from "../RegistryEntityIcon";
const { NEXT_PUBLIC_DATA_REGISTRY_NAME } = allEnv();
export default function RelationEntity({ entity }) {
    const { name, scope, type } = entity;
    const [relation, setRelation] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedRelation, setEditedRelation] = useState(null);
    const [loading, setLoading] = useState(false);
    const updateRelation = ({ path, value }) => {
        let newRelation = _.cloneDeep(editedRelation);
        _.set(newRelation, path, value);
        setEditedRelation(newRelation);
    };
    const darkMode = useAppStore((state) => state.dark_mode);
    const path = [scope.substring(1), type, name]
        .filter((str) => !_.isEmpty(str))
        .join("/");
    const url = _.replace(
        `/registry/${NEXT_PUBLIC_DATA_REGISTRY_NAME}/${path}`,
        "/source/",
        "/data/"
    );
    useEffect(() => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                setRelation(result);
                setEditedRelation(result);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [entity]);
    const handleDiscard = () => {
        setEditedRelation(relation);
        setIsEditing(false);
    };
    const handleSave = () => {
        setLoading(true);
        axios
            .put(url, {
                name: editedRelation.name,
                description: editedRelation.description,
            })
            .finally(() => {
                setLoading(false);
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
                {!_.isEmpty(relation) && (
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={{ position: "absolute", right: 20 }}
                    >
                        <EntityActions
                            loading={loading}
                            handleSave={handleSave}
                            handleDiscard={handleDiscard}
                            entity={relation}
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
                        content={_.get(editedRelation, "icon", null)}
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
                        <div>{_.get(editedRelation, "type")}</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(editedRelation, "name")}
                        </div>
                    </div>
                </div>
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityDescription
                    isEditing={isEditing}
                    updateEntity={updateRelation}
                    entity={editedRelation}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityProperties
                    isEditing={false}
                    updateEntity={updateRelation}
                    entity={editedRelation}
                    loading={loading}
                />
            </div>
        </div>
    );
}

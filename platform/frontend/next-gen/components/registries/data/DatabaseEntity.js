import {
    ENTITY_TYPE_LOOKUP,
    HEX_TRANSPARENCY,
    MAIN_INFO_STYLES,
    REGISTRY_ENTITY_ICON_WRAPPER_STYLES,
} from "@/components/constants";
import { useGridContainerContext } from "@/components/contexts/GridContainerContext";
import { FAIcon } from "@/components/FAIcon";
import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { Classes, Colors, EntityTitle, H3 } from "@blueprintjs/core";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { allEnv } from "next-runtime-env";
import { useEffect, useState } from "react";
import EntityDescription from "../attributes/EntityDescription";
import EntityProperties from "../attributes/EntityProperties";
import EntityActions from "../EntityActions";
import EntityDisplayName from "../EntityDisplayName";
import Leaves from "../Leaves";
import RegistryEntityIcon from "../RegistryEntityIcon";
const { NEXT_PUBLIC_DATA_REGISTRY_NAME } = allEnv();
export default function DatabaseEntity({ entity, addCrumb, backCrumb }) {
    const { name, scope, type } = entity;
    const [database, setDatabase] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedDatabase, setEditedDatabase] = useState(null);
    const [loading, setLoading] = useState(false);
    const updateDatabase = ({ path, value }) => {
        let newDatabase = _.cloneDeep(editedDatabase);
        _.set(newDatabase, path, value);
        setEditedDatabase(newDatabase);
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
    const setContainerHeader = useGridStore(
        (state) => state.setContainerHeader
    );
    const { gridContainerId } = useGridContainerContext();
    useEffect(() => {
        setContainerHeader({
            id: gridContainerId,
            title: <EntityDisplayName entity={database} />,
            icon: _.get(ENTITY_TYPE_LOOKUP, [type, "icon"], null),
        });
    }, [database]);
    const fetchDatabase = () => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                setDatabase(result);
                setEditedDatabase(result);
            })
            .finally(() => {
                setLoading(false);
            });
    };
    useEffect(() => {
        fetchDatabase();
    }, [entity]);
    const handleDiscard = () => {
        setEditedDatabase(database);
        setIsEditing(false);
    };
    const handleSave = () => {
        setLoading(true);
        axios
            .put(url, {
                name: editedDatabase.name,
                description: editedDatabase.description,
            })
            .finally(() => {
                setLoading(false);
            });
    };
    const onDelete = () => {
        setLoading(true);
        axios.delete(url).finally(() => {
            setLoading(false);
            backCrumb();
        });
    };
    const onSynchronize = () => {
        setLoading(true);
        axios.put(`${url}/sync`).finally(() => {
            setLoading(false);
            fetchDatabase();
        });
    };
    const onEnrichMetadata = () => {
        setLoading(true);
        axios.put(`${url}/metadata`).finally(() => {
            setLoading(false);
            fetchDatabase();
        });
    };
    const onCollectStats = () => {
        setLoading(true);
        axios.put(`${url}/stats`).finally(() => {
            setLoading(false);
            fetchDatabase();
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
                {!_.isEmpty(database) && (
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={{ position: "absolute", right: 20 }}
                    >
                        <EntityActions
                            loading={loading}
                            handleSave={handleSave}
                            handleDiscard={handleDiscard}
                            entity={database}
                            isEditing={isEditing}
                            setIsEditing={setIsEditing}
                            onDelete={onDelete}
                            onSynchronize={onSynchronize}
                            onEnrichMetadata={onEnrichMetadata}
                            onCollectStats={onCollectStats}
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
                        type={type}
                        content={_.get(editedDatabase, "icon", null)}
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
                        <div>{_.get(editedDatabase, "type")}</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(editedDatabase, "name")}
                        </div>
                    </div>
                </div>
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityDescription
                    isEditing={isEditing}
                    updateEntity={updateDatabase}
                    entity={editedDatabase}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityProperties
                    isEditing={false}
                    updateEntity={updateDatabase}
                    entity={editedDatabase}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <div style={{ marginBottom: 10 }}>
                    <EntityTitle
                        icon={
                            <FAIcon
                                icon={ENTITY_TYPE_LOOKUP["collection"].icon}
                                size={25}
                            />
                        }
                        heading={H3}
                        title="Collections"
                    />
                </div>
                <div
                    style={{
                        display: "flex",
                        gap: 10,
                        flexDirection: "column",
                    }}
                >
                    <Leaves
                        isEditing={isEditing}
                        loading={loading}
                        addCrumb={addCrumb}
                        list={_.values(
                            _.get(database, "contents.collection", {})
                        )}
                    />
                </div>
            </div>
        </div>
    );
}

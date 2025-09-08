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
export default function CollectionEntity({ entity, addCrumb }) {
    const { name, scope, type } = entity;
    const [collection, setCollection] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [editedCollection, setEditedCollection] = useState(null);
    const [loading, setLoading] = useState(false);
    const updateCollection = ({ path, value }) => {
        let newCollection = _.cloneDeep(editedCollection);
        _.set(newCollection, path, value);
        setEditedCollection(newCollection);
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
            title: <EntityDisplayName entity={collection} />,
            icon: _.get(ENTITY_TYPE_LOOKUP, [type, "icon"], null),
        });
    }, [collection]);
    const fetchCollection = () => {
        setLoading(true);
        axios
            .get(url)
            .then((response) => {
                const result = _.get(response, "data.result", null);
                setCollection(result);
                setEditedCollection(result);
            })
            .finally(() => {
                setLoading(false);
            });
    };
    const onSynchronize = () => {
        setLoading(true);
        axios.put(`${url}/sync`).finally(() => {
            setLoading(false);
            fetchCollection();
        });
    };
    useEffect(() => {
        fetchCollection();
    }, [entity]);
    const handleDiscard = () => {
        setEditedCollection(collection);
        setIsEditing(false);
    };
    const handleSave = () => {
        setLoading(true);
        axios
            .put(url, {
                name: editedCollection.name,
                description: editedCollection.description,
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
                {!_.isEmpty(collection) && (
                    <div
                        className={loading ? Classes.SKELETON : null}
                        style={{ position: "absolute", right: 20 }}
                    >
                        <EntityActions
                            loading={loading}
                            handleSave={handleSave}
                            handleDiscard={handleDiscard}
                            entity={collection}
                            isEditing={isEditing}
                            setIsEditing={setIsEditing}
                            onSynchronize={onSynchronize}
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
                        content={_.get(editedCollection, "icon", null)}
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
                        <div>{_.get(editedCollection, "type")}</div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{ fontWeight: 600 }}
                        >
                            {_.get(editedCollection, "name")}
                        </div>
                    </div>
                </div>
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityDescription
                    isEditing={isEditing}
                    updateEntity={updateCollection}
                    entity={editedCollection}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <EntityProperties
                    isEditing={false}
                    updateEntity={updateCollection}
                    entity={editedCollection}
                    loading={loading}
                />
            </div>
            <div style={{ marginTop: 20 }}>
                <div style={{ marginBottom: 10 }}>
                    <EntityTitle
                        icon={
                            <FAIcon
                                icon={ENTITY_TYPE_LOOKUP["entity"].icon}
                                size={25}
                            />
                        }
                        heading={H3}
                        title="Entities"
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
                            _.get(collection, "contents.entity", {})
                        )}
                    />
                </div>
            </div>
            <div style={{ marginTop: 20 }}>
                <div style={{ marginBottom: 10 }}>
                    <EntityTitle
                        icon={
                            <FAIcon
                                icon={ENTITY_TYPE_LOOKUP["relation"].icon}
                                size={25}
                            />
                        }
                        heading={H3}
                        title="Relations"
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
                            _.get(collection, "contents.relation", {})
                        )}
                    />
                </div>
            </div>
        </div>
    );
}

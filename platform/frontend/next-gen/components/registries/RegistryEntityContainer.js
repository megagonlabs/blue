import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { Colors, Overlay2 } from "@blueprintjs/core";
import _ from "lodash";
import { useCallback, useEffect, useRef, useState } from "react";
import { useShallow } from "zustand/react/shallow";
import IconEditor from "../IconEditor";
import { ENTITY_TYPE_LOOKUP } from "../constants";
import { useGridContainerContext } from "../contexts/GridContainerContext";
import withAutoSizer from "../hocs/withAutoSizer";
import Breadcrumbs from "./Breadcrumbs";
import NewEntity from "./NewEntity";
import AgentEntity from "./agents/AgentEntity";
import AgentGroupEntity from "./agents/AgentGroupEntity";
import AgentList from "./agents/AgentList";
import AgentTree from "./agents/AgentTree";
import CollectionEntity from "./data/CollectionEntity";
import DatabaseEntity from "./data/DatabaseEntity";
import EntityEntity from "./data/EntityEntity";
import RelationEntity from "./data/RelationEntity";
import SourceEntity from "./data/SourceEntity";
import SourceList from "./data/SourceList";
import InputEntity from "./inputs/InputEntity";
import ModelEntity from "./models/ModelEntity";
import ModelList from "./models/ModelList";
import OperatorEntity from "./operators/OperatorEntity";
import OperatorList from "./operators/OperatorList";
import OutputEntity from "./outputs/OutputEntity";
import ServerEntity from "./tools/ServerEntity";
import ToolEntity from "./tools/ToolEntity";
import ToolList from "./tools/ToolList";
function RegistryEntityContainer({
    width,
    height,
    entity,
    registry,
    duplicate = false,
    registryCrumb = false,
}) {
    const [breadcrumbs, setBreadcrumbs] = useState([]);
    const [duplicated, setDuplicated] = useState(false);
    const darkMode = useAppStore((state) => state.dark_mode);
    const { gridContainerId } = useGridContainerContext();
    const { replaceContainer, removeContainer } = useGridStore(
        useShallow((state) => ({
            replaceContainer: state.replaceContainer,
            removeContainer: state.removeContainer,
        }))
    );
    useEffect(() => {
        const { type } = entity;
        let crumbs = [];
        if (registryCrumb) {
            const REGISTRY_LIST_LOOKUP = {
                agent: { list: <AgentList />, title: "Agent Registry" },
                source: {
                    name: "data",
                    list: <SourceList />,
                    title: "Data Registry",
                },
                model: { list: <ModelList />, title: "Model Registry" },
                server: {
                    tool: {
                        name: "tool",
                        list: <ToolList />,
                        title: "Tool Registry",
                    },
                    operator: {
                        name: "operator",
                        list: <OperatorList />,
                        title: "Operator Registry",
                    },
                },
            };
            let calculatedType = type,
                path = [type];
            if (_.isEqual(type, "server")) {
                calculatedType = registry;
                path = ["server", registry];
            }
            if (_.has(REGISTRY_LIST_LOOKUP, path)) {
                const { list, title } = _.get(REGISTRY_LIST_LOOKUP, path, {});
                crumbs.push({
                    type: "registry",
                    name: _.get(
                        REGISTRY_LIST_LOOKUP,
                        [...path, "name"],
                        calculatedType
                    ),
                    content: list,
                    listType: calculatedType,
                    title,
                });
            }
        }
        crumbs.push(entity);
        setBreadcrumbs(normalizeCrumbs(crumbs));
    }, [entity]);
    const normalizeCrumbs = useCallback(
        (list) => {
            let next = _.cloneDeep(list);
            _.remove(
                next,
                (element) =>
                    !registryCrumb && _.isEqual(element.type, "registry")
            );
            for (let i = 0; i < _.size(next); i++) {
                _.set(next, [i, "start"], _.isEqual(i, 0));
                _.set(next, [i, "end"], _.isEqual(i, _.size(next) - 1));
                _.set(next, [i, "index"], i);
            }
            return next;
        },
        [registryCrumb]
    );
    const scrollableRef = useRef(null);
    const scrollToTop = () => {
        if (scrollableRef.current) {
            scrollableRef.current.scrollTop = 0;
        }
    };
    const toCrumb = (index) => {
        setBreadcrumbs(normalizeCrumbs(_.slice(breadcrumbs, 0, index + 1)));
        scrollToTop();
    };
    const addCrumb = (entity) => {
        setBreadcrumbs(normalizeCrumbs([...breadcrumbs, entity]));
        scrollToTop();
    };
    const backCrumb = () => {
        const index = Math.max(0, _.size(breadcrumbs) - 1);
        const newCrumbs = normalizeCrumbs(_.slice(breadcrumbs, 0, index));
        if (_.isEmpty(newCrumbs)) {
            removeContainer(gridContainerId);
        } else {
            if (_.isEqual(_.size(newCrumbs), 1)) {
                const {
                    type: crumbType,
                    content,
                    title,
                    listType,
                } = newCrumbs[0];
                if (_.isEqual(crumbType, "registry")) {
                    const icon = _.get(
                        ENTITY_TYPE_LOOKUP,
                        [listType, "icon"],
                        null
                    );
                    replaceContainer({
                        id: gridContainerId,
                        content,
                        icon,
                        title,
                    });
                    return;
                }
            }
            scrollToTop();
            setBreadcrumbs(normalizeCrumbs(_.slice(breadcrumbs, 0, index)));
        }
    };
    const current = _.last(breadcrumbs);
    const type = _.get(current, "type", null);
    const [icon, setIcon] = useState(null);
    const [showIconEditor, setShowIconEditor] = useState(false);
    const [showNewEntity, setShowNewEntity] = useState(false);
    const [newEntityType, setNewEntityType] = useState(null);
    const breaker = useRef(true);
    const callback = (entity) => {
        setShowNewEntity(false);
        addCrumb(entity);
    };
    const onDuplicate = (entity) => {
        setDuplicated(true);
        let crumbs = [entity];
        _.set(crumbs, [0, "start"], true);
        _.set(crumbs, [0, "end"], true);
        setBreadcrumbs(crumbs);
    };
    return (
        <div
            style={{
                width,
                height,
                position: "relative",
                backgroundColor: darkMode ? Colors.BLACK : null,
            }}
        >
            <Overlay2
                onClose={() => {
                    setShowNewEntity(false);
                    if (_.isEqual(type, "agent_group")) {
                        breaker.current = false;
                    }
                }}
                isOpen={showNewEntity}
                usePortal={false}
                enforceFocus={false}
                transitionDuration={0}
            >
                <div
                    className="custom-card center-center"
                    style={{
                        width: 800,
                        padding: 20,
                        overflowY: "auto",
                        height: "calc(100% - 40px)",
                        maxWidth: "calc(100% - 40px)",
                    }}
                >
                    {_.isEqual(type, "agent_group") ? (
                        <AgentTree entity={entity} />
                    ) : (
                        <NewEntity
                            callback={callback}
                            parent={current}
                            type={newEntityType}
                        />
                    )}
                </div>
            </Overlay2>
            <Overlay2
                onClose={() => {
                    setShowIconEditor(false);
                }}
                isOpen={showIconEditor}
                usePortal={false}
                enforceFocus={false}
                transitionDuration={0}
            >
                <div
                    className="custom-card center-center"
                    style={{
                        width: 800,
                        height: "calc(100% - 40px)",
                        maxWidth: "calc(100% - 40px)",
                    }}
                >
                    <IconEditor
                        setShowIconEditor={setShowIconEditor}
                        content={icon}
                        setIcon={setIcon}
                    />
                </div>
            </Overlay2>
            <div
                className="full-parent-dimension"
                ref={scrollableRef}
                style={{
                    padding: 20,
                    position: "relative",
                    overflowY: "auto",
                }}
            >
                {duplicate && !duplicated ? (
                    <NewEntity
                        duplicateEntity={entity}
                        callback={onDuplicate}
                        registry={registry}
                    />
                ) : (
                    <>
                        <Breadcrumbs crumbs={breadcrumbs} toCrumb={toCrumb} />
                        <div
                            style={{ marginTop: !_.isEmpty(breadcrumbs) && 20 }}
                        >
                            {_.isEqual(type, "agent") && (
                                <AgentEntity
                                    setShowNewEntity={setShowNewEntity}
                                    setNewEntityType={setNewEntityType}
                                    icon={icon}
                                    setIcon={setIcon}
                                    setShowIconEditor={setShowIconEditor}
                                    addCrumb={addCrumb}
                                    backCrumb={backCrumb}
                                    entity={current}
                                />
                            )}
                            {_.isEqual(type, "agent_group") && (
                                <AgentGroupEntity
                                    icon={icon}
                                    setIcon={setIcon}
                                    setShowIconEditor={setShowIconEditor}
                                    addCrumb={addCrumb}
                                    backCrumb={backCrumb}
                                    entity={current}
                                    setShowAgentTree={setShowNewEntity}
                                    breaker={breaker}
                                />
                            )}
                            {_.isEqual(type, "input") && (
                                <InputEntity
                                    entity={current}
                                    backCrumb={backCrumb}
                                />
                            )}
                            {_.isEqual(type, "output") && (
                                <OutputEntity
                                    entity={current}
                                    backCrumb={backCrumb}
                                />
                            )}
                            {_.isEqual(type, "source") && (
                                <SourceEntity
                                    icon={icon}
                                    setIcon={setIcon}
                                    setShowIconEditor={setShowIconEditor}
                                    addCrumb={addCrumb}
                                    backCrumb={backCrumb}
                                    entity={current}
                                />
                            )}
                            {_.isEqual(type, "database") && (
                                <DatabaseEntity
                                    addCrumb={addCrumb}
                                    entity={current}
                                    backCrumb={backCrumb}
                                />
                            )}
                            {_.isEqual(type, "collection") && (
                                <CollectionEntity
                                    addCrumb={addCrumb}
                                    entity={current}
                                />
                            )}
                            {_.isEqual(type, "entity") && (
                                <EntityEntity entity={current} />
                            )}
                            {_.isEqual(type, "relation") && (
                                <RelationEntity entity={current} />
                            )}
                            {_.isEqual(type, "operator") && (
                                <OperatorEntity
                                    icon={icon}
                                    setIcon={setIcon}
                                    setShowIconEditor={setShowIconEditor}
                                    entity={current}
                                    backCrumb={backCrumb}
                                />
                            )}
                            {_.isEqual(type, "model") && (
                                <ModelEntity
                                    icon={icon}
                                    setIcon={setIcon}
                                    setShowIconEditor={setShowIconEditor}
                                    entity={current}
                                />
                            )}
                            {_.isEqual(type, "server") && (
                                <ServerEntity
                                    registry={registry}
                                    entity={current}
                                    addCrumb={addCrumb}
                                    backCrumb={backCrumb}
                                    setShowNewEntity={setShowNewEntity}
                                    setNewEntityType={setNewEntityType}
                                />
                            )}
                            {_.isEqual(type, "tool") && (
                                <ToolEntity
                                    entity={current}
                                    addCrumb={addCrumb}
                                    backCrumb={backCrumb}
                                    setShowNewEntity={setShowNewEntity}
                                    setNewEntityType={setNewEntityType}
                                />
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
export default withAutoSizer(RegistryEntityContainer);

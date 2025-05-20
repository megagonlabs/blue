import { useAppStore } from "@/stores/app-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { Colors, Overlay2 } from "@blueprintjs/core";
import _ from "lodash";
import { useEffect, useState } from "react";
import IconEditor from "../IconEditor";
import { useContainerContext } from "../contexts/ContainerContext";
import withAutoSizer from "../hocs/withAutoSizer";
import Breadcrumbs from "./Breadcrumbs";
import NewEntity from "./NewEntity";
import AgentEntity from "./agents/AgentEntity";
import CollectionEntity from "./data/CollectionEntity";
import DatabaseEntity from "./data/DatabaseEntity";
import EntityEntity from "./data/EntityEntity";
import RelationEntity from "./data/RelationEntity";
import SourceEntity from "./data/SourceEntity";
import InputEntity from "./inputs/InputEntity";
import ModelEntity from "./models/ModelEntity";
import OperatorEntity from "./operators/OperatorEntity";
import OutputEntity from "./outputs/OutputEntity";
function RegistryEntityContainer({ width, height, entity }) {
    const [breadcrumbs, setBreadcrumbs] = useState([]);
    const darkMode = useAppStore((state) => state.dark_mode);
    const { containerId } = useContainerContext();
    const removeContainer = useGridStore((state) => state.removeContainer);
    useEffect(() => {
        let crumbs = [entity];
        _.set(crumbs, [0, "start"], true);
        _.set(crumbs, [0, "end"], true);
        setBreadcrumbs(crumbs);
    }, [entity]);
    const normalizeCrumbs = (list) => {
        let next = _.cloneDeep(list);
        for (let i = 0; i < _.size(next); i++) {
            _.set(next, [i, "start"], _.isEqual(i, 0));
            _.set(next, [i, "end"], _.isEqual(i, _.size(next) - 1));
            _.set(next, [i, "index"], i);
        }
        return next;
    };
    const toCrumb = (index) => {
        setBreadcrumbs(normalizeCrumbs(_.slice(breadcrumbs, 0, index + 1)));
    };
    const addCrumb = (entity) => {
        setBreadcrumbs(normalizeCrumbs([...breadcrumbs, entity]));
    };
    const backCrumb = () => {
        if (_.size(breadcrumbs) > 1) {
            const index = Math.max(0, _.size(breadcrumbs) - 1);
            setBreadcrumbs(normalizeCrumbs(_.slice(breadcrumbs, 0, index)));
        } else {
            removeContainer(containerId);
        }
    };
    const current = _.last(breadcrumbs);
    const type = _.get(current, "type", null);
    const [icon, setIcon] = useState(null);
    const [showIconEditor, setShowIconEditor] = useState(false);
    const [showNewEntity, setShowNewEntity] = useState(false);
    const [newEntityType, setNewEntityType] = useState(null);
    const callback = (entity) => {
        setShowNewEntity(false);
        addCrumb(entity);
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
                    <NewEntity
                        callback={callback}
                        parent={current}
                        type={newEntityType}
                        addCrumb={addCrumb}
                    />
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
                style={{
                    padding: 20,
                    position: "relative",
                    overflowY: "auto",
                }}
            >
                <Breadcrumbs crumbs={breadcrumbs} toCrumb={toCrumb} />
                <div style={{ marginTop: !_.isEmpty(breadcrumbs) && 20 }}>
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
                    {_.isEqual(type, "input") && (
                        <InputEntity entity={current} backCrumb={backCrumb} />
                    )}
                    {_.isEqual(type, "output") && (
                        <OutputEntity entity={current} backCrumb={backCrumb} />
                    )}
                    {_.isEqual(type, "source") && (
                        <SourceEntity
                            icon={icon}
                            setIcon={setIcon}
                            setShowIconEditor={setShowIconEditor}
                            addCrumb={addCrumb}
                            entity={current}
                        />
                    )}
                    {_.isEqual(type, "database") && (
                        <DatabaseEntity addCrumb={addCrumb} entity={current} />
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
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(RegistryEntityContainer);

import { useAppStore } from "@/stores/app-store";
import { Colors } from "@blueprintjs/core";
import _ from "lodash";
import { useEffect, useState } from "react";
import { useContainerContext } from "../contexts/ContainerContext";
import withAutoSizer from "../hocs/withAutoSizer";
import Breadcrumbs from "./Breadcrumbs";
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
    const { containerId } = useContainerContext();
    const darkMode = useAppStore((state) => state.dark_mode);
    useEffect(() => {
        const { name, type, scope } = entity;
        let crumbs = [{ name, type, scope }];
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
        const { name, type, scope } = entity;
        setBreadcrumbs(
            normalizeCrumbs([...breadcrumbs, { name, type, scope }])
        );
    };
    const current = _.last(breadcrumbs);
    const type = _.get(current, "type", null);
    return (
        <div
            style={{
                width,
                height,
                backgroundColor: darkMode ? Colors.BLACK : null,
            }}
        >
            <div
                className="full-parent-dimension"
                style={{
                    padding: 20,
                    position: "relative",
                    overflowY: "auto",
                }}
            >
                <Breadcrumbs crumbs={breadcrumbs} toCrumb={toCrumb} />
                <div style={{ marginTop: 20 }}>
                    {_.isEqual(type, "agent") && (
                        <AgentEntity addCrumb={addCrumb} entity={current} />
                    )}
                    {_.isEqual(type, "input") && (
                        <InputEntity entity={current} />
                    )}
                    {_.isEqual(type, "output") && (
                        <OutputEntity entity={current} />
                    )}
                    {_.isEqual(type, "source") && (
                        <SourceEntity addCrumb={addCrumb} entity={current} />
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
                        <OperatorEntity entity={current} />
                    )}
                    {_.isEqual(type, "model") && (
                        <ModelEntity entity={current} />
                    )}
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(RegistryEntityContainer);

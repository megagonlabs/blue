import { Classes } from "@blueprintjs/core";
import { useContext, useEffect, useRef, useCallback, useState } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import classNames from "classnames";
import { Row, Col, Container } from "react-grid-system";
import { AppContext } from "../app-context";
import {
    Intent,
    Card,
    Tag,
    H5,
    ButtonGroup,
    Button,
    Dialog,
    Callout,
} from "@blueprintjs/core";
import {
    BUTTON_WITH_TOOLTIP2,
    DARK_THEME_CLASS,
    DEBOUNCE_INTERVAL,
} from "../constant";
import axios from "axios";
import _ from "lodash";
import { actionToaster, createToast } from "../toaster";
import { Tooltip } from "@blueprintjs/core";
import Link from "next/link";
import { Icon, IconSize } from "@blueprintjs/core";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function AgentList({ setIsSearchOptionOpen }) {
    const cardListClassName = `${Classes.CARD} ${Classes.CARD_LIST} ${Classes.CARD_LIST_BORDERED}`;
    const { appState } = useContext(AppContext);
    const [isLoading, setIsLoading] = useState(true);
    const fixedSizeListRef = useRef();

    const [agents, setAgents] = useState([]);
    const [deleteId, setDeleteId] = useState(null);
    const [editId, setEditId] = useState(null);
    const [entityName, setEntityName] = useState("");
    const [isDeleting, setIsDeleting] = useState(false);
    const [isFormDialogOpen, setIsFormDialogOpen] = useState(false);

    useEffect(() => {
    }, [fixedSizeListRef]);

    const deleteAgent = () => {
        setIsDeleting(true);
        axios
            .delete("/agents/agent", {
                params: {
                    agentID: deleteId,
                },
            })
            .then((response) => {
                setIsDeleting(false);
                setDeleteId(null);
                const resultId = _.get(response, "data.id", null);
                if (!_.isNil(resultId)) {
                    setAgents(
                        agents.filter(
                            (agent) => !_.isEqual(resultId, agent.id)
                        )
                    );
                }
            })
            .catch((error) => {
                setIsDeleting(false);
                actionToaster.show(
                    createToast({
                        className: themeClass,
                        intent: Intent.DANGER,
                        message: (
                            <div className="bp4-text-large">
                                {error.name}:
                                <br />
                                {_.get(
                                    error,
                                    "response.data.message",
                                    error.message
                                )}
                            </div>
                        ),
                    })
                );
            });
    };
    useEffect(() => {
        setIsFormDialogOpen(!_.isNil(editId));
    }, [editId]);
    const setAgent = (agent) => {
        var nextAgents = [...agents];
        for (var i = 0; i < nextAgents.length; i++) {
            const agentId = _.get(agent, "id", null);
            if (_.isEqual(agentId, nextAgents[i].id)) {
                nextAgents[i] = agent;
            }
        }
        setAgents(nextAgents);
    };
    const fetchEntities = () => {
        setIsLoading(true);
        axios
            .get("/agents", {
            })
            .then((response) => {
                // sort
                response.data.list.sort((a, b) => (a.name > b.name) ? 1 : -1)
                setAgents(response.data.list);
                setIsLoading(false);
            })
            .catch((error) => {
                actionToaster.show(
                    createToast({
                        intent: Intent.DANGER,
                        message: (
                            <div className="bp4-text-large">
                                {error.name}:
                                <br />
                                {_.get(
                                    error,
                                    "response.data.message",
                                    error.message
                                )}
                            </div>
                        ),
                    })
                );
            });
    };
    useEffect(() => {
        fetchEntities();
    }, []);
    if (_.isEmpty(agents)) {
        if (isLoading)
            return (
                <div
                    className="bp4-skeleton"
                    style={{
                        height: 124,
                        margin: "20px 20px 0px 20px",
                    }}
                />
            );
        const color = _.isEqual(themeClass, DARK_THEME_CLASS)
            ? "#abb3bf"
            : "#5f6b7c";
        return (
            <div style={{ marginLeft: 20, marginTop: 20 }}>
                <Icon icon="more" />
                <div
                    style={{
                        color: color,
                        marginBottom: 20,
                        marginTop: 10,
                    }}
                >
                    <H5
                        style={{
                            color: color,
                        }}
                    >
                        No agents matched your search.
                    </H5>
                    <div>Try using search options.</div>
                </div>
                <Button
                    onClick={() => setIsSearchOptionOpen(true)}
                    text="Show search options"
                />
            </div>
        );
    }
    return (
        <>
            <Container fluid style={{ padding: "20px 20px 10px 21px" }}>
                <Row gutterWidth={10}>
                    {agents.map((agent) => (
                        <Col
                            sm={12}
                            md={6}
                            lg={4}
                            xl={3}
                            xxl={2}
                            key={`app-agents-agentlist-${agent.name}`}
                        >
                            <Link
                                href={`/agents?agentID=${agent.name}`}
                            >
                                <Card
                                    interactive
                                    className="entity-card"
                                    style={{
                                        overflow: "hidden",
                                        marginBottom: 10,
                                        padding: 10,
                                        height: "150px",
                                        position: "relative",
                                        borderRadius: "5px"
                                    }}
                                >
                                    <H5
                                        className={classNames({
                                            "bp4-text-overflow-ellipsis": true,
                                            "margin-0": true,
                                            "bp4-skeleton": isLoading,
                                        })}
                                    >
                                        {_.get(agent, "name", "-")}
                                    </H5>
                                    <Tag
                                        style={{ marginTop: 5 }}
                                        intent={Intent.PRIMARY}
                                        minimal
                                        round
                                    >
                                        {_.get(agent, "properties.image", "-")}
                                    </Tag>
                                    <div
                                        className={classNames({
                                            "bp4-text-muted": true,
                                            "bp4-skeleton": isLoading,
                                        })}
                                        style={{
                                            marginTop: 5,
                                            maxHeight: 80,
                                            lineHeight: "20px",
                                            overflow: "hidden",
                                        }}
                                    >
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                        >
                                            {_.isEmpty(agent.description)
                                                ? ""
                                                : agent.description}
                                        </ReactMarkdown>
                                    </div>
                                    <Card
                                        className="bp4-elevation-4 entity-actions"
                                        style={{
                                            position: "absolute",
                                            bottom: 0,
                                            textAlign: "right",
                                            padding: 5,
                                            right: 0,
                                            borderRadius: 0,
                                            borderTopLeftRadius: 2,
                                            borderBottomRightRadius: 2,
                                            display: "none",
                                            backgroundColor: "transparent",
                                            boxShadow: "none",
                                            border: "none"
                                        }}
                                    >
                                        <ButtonGroup
                                            large
                                            className={
                                                isLoading
                                                    ? "bp4-skeleton"
                                                    : null
                                            }
                                        >
    
                                            <Tooltip
                                                {...BUTTON_WITH_TOOLTIP2}
                                                content="Edit"
                                            >
                                                <Button
                                                    onClick={(event) => {
                                                        event.stopPropagation();
                                                        setEditId(
                                                            agent.id
                                                        );
                                                        setEntityName(
                                                            agent.name
                                                        );
                                                    }}
                                                    intent={Intent.PRIMARY}
                                                    minimal
                                                    icon={
                                                        <Icon icon="edit" />
                                                    }
                                                />
                                            </Tooltip>
                                            <Tooltip
                                                {...BUTTON_WITH_TOOLTIP2}
                                                content="Delete"
                                            >
                                                <Button
                                                    onClick={(event) => {
                                                        event.stopPropagation();
                                                        setDeleteId(
                                                            agent.id
                                                        );
                                                        setEntityName(
                                                            agent.name
                                                        );
                                                    }}
                                                    intent={Intent.DANGER}
                                                    minimal
                                                    icon={
                                                        <Icon icon="cross" />
                                                    }
                                                />
                                            </Tooltip>
                                        </ButtonGroup>
                                    </Card>
                                </Card>
                            </Link>
                        </Col>
                    ))}
                    <Col
                        sm={12}
                        md={6}
                        lg={4}
                        xl={3}
                        xxl={2}
                        key={`app-projects-projectlist-create`}
                    >
                        <Card
                            onClick={() => {
                                setIsFormDialogOpen(true);
                                setEditId(null);
                                setEntityName("");
                            }}
                            interactive
                            style={{
                                padding: 10,
                                marginBottom: 10,
                                width: "40px",
                                height: "40px",
                                position: "relative",
                                borderRadius: "40px"
                            }}
                        >
                            <div
                                style={{
                                    position: "absolute",
                                    top: "0%",
                                    left: "0%",
                                    textAlign: "center",
                                }}
                            >
                                <Button
                                    className="none-pointer-events"
                                    intent={Intent.PRIMARY}
                                    icon={<Icon icon="plus" />}
                                    minimal
                                    large
                                    text=""
                                />
                            </div>
                        </Card>
                    </Col>
                </Row>
            </Container>
        </>
    );
}

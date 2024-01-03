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
import _ from "lodash";

import { Tooltip } from "@blueprintjs/core";
import Link from "next/link";
import { Icon, IconSize } from "@blueprintjs/core";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function AgentList() {
    const cardListClassName = `${Classes.CARD} ${Classes.CARD_LIST} ${Classes.CARD_LIST_BORDERED}`;
    const { appState } = useContext(AppContext);
    const [isLoading, setIsLoading] = useState(true);
    const [agents, setAgents] = useState([{"name":"TitleRecommender","type":"agent","scope":"\\\/","description":"Recommends next title given a title","properties":{"image":"blue-agent-simple_graph:latest"}},{"name":"Neo4J","type":"agent","scope":"\\\/","description":"Execute graph database queries","properties":{"image":"blue-agent-neo4j:latest"}},{"name":"OpenAITripleExtractor","type":"agent","scope":"\\\/","description":"Given a text extract entities and relations in the form of source and target entities and relationship between them using OpenAI","properties":{"image":"blue-agent-openai:latest"}},{"name":"OpenAINeo4JQuery","type":"agent","scope":"\\\/","description":"Given triples with source and target entities and relationships, transform triples to neo4j querys that can be executed","properties":{"image":"blue-agent-openai:latest"}},{"name":"Recorder","type":"agent","scope":"\\\/","description":"Scan JSON documents and find matched entities","properties":{"image":"blue-agent-recorder:latest"}},{"name":"Rationalizer","type":"agent","scope":"\\\/","description":"Given one or more text documents rationalize a relation between said documents","properties":{"image":"blue-agent-rationalizer:latest"}},{"name":"KnowledgeGrounding","type":"agent","scope":"\\\/","description":"Given a text identify missing knowledge to explain","properties":{"image":"blue-agent-knowledge_grounding:latest"}},{"name":"JobRecommender","type":"agent","scope":"\\\/","description":"Given a resume, recommend a job","properties":{"image":"blue-agent-job_recommender:latest"}},{"name":"CareerRecommender","type":"agent","scope":"\\\/","description":"Given a resume, give career advice","properties":{"image":"blue-agent-career_recommender:latest"}},{"name":"JobSearch","type":"agent","scope":"\\\/","description":"Search job descriptions database given keywords","properties":{"image":"blue-agent-job_search:latest"}},{"name":"JobCandidateMatch","type":"agent","scope":"\\\/","description":"Given a resume and job description, predict match","properties":{"image":"blue-agent-match:latest"}},{"name":"Explainer","type":"agent","scope":"\\\/","description":"Given a resume and a job description explain match","properties":{"image":"blue-agent-explainer:latest"}},{"name":"CandidateSearch","type":"agent","scope":"\\\/","description":"Search candidate resume database given keywords","properties":{"image":"blue-agent-candidate_search:latest"}}]);
    const fixedSizeListRef = useRef();
    
    useEffect(() => {
        
    }, [fixedSizeListRef]);
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

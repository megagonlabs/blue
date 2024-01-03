import {
    Button,
    ButtonGroup,
    Card,
    H5,
    Icon,
    Intent,
    Popover,
    Tag,
} from "@blueprintjs/core";
import classNames from "classnames";
import _ from "lodash";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Col, Container, Row } from "react-grid-system";
import { BUTTON_WITH_TOOLTIP2 } from "../constant";
export default function DataSourceList() {
    const [datasources, setDataSources] = useState([
        {
            name: "indeed_mongodb",
            type: "source",
            scope: "\\/",
            description: "Source for all indeed original data",
            properties: {
                connection: {
                    host: "localhost",
                    port: 27017,
                    protocol: "mongodb",
                },
            },
        },
        {
            name: "indeed_yellowhat",
            type: "source",
            scope: "\\/",
            description: "Source for all indeed yellowhat data",
            properties: {
                connection: {
                    host: "3.17.140.111",
                    port: 7687,
                    protocol: "bolt",
                },
            },
        },
    ]);
    const fixedSizeListRef = useRef();
    useEffect(() => {}, [fixedSizeListRef]);
    return (
        <>
            <Container fluid style={{ padding: "20px 20px 10px 21px" }}>
                <Row gutterWidth={10}>
                    {datasources.map((datasource) => (
                        <Col
                            sm={12}
                            md={6}
                            lg={4}
                            xl={3}
                            xxl={2}
                            key={`app-datasources-datasourcelist-${datasource.id}`}
                        >
                            <Link
                                href={`/datasources?datasourceID=${datasource.id}`}
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
                                        borderRadius: "5px",
                                    }}
                                >
                                    <H5
                                        className={classNames({
                                            "bp4-text-overflow-ellipsis": true,
                                            "margin-0": true,
                                        })}
                                    >
                                        {_.get(datasource, "name", "-")}
                                    </H5>
                                    <Tag
                                        style={{ marginTop: 5 }}
                                        intent={Intent.PRIMARY}
                                        minimal
                                        round
                                    >
                                        {_.get(
                                            datasource,
                                            "properties.connection.protocol",
                                            "-"
                                        ) +
                                            "://" +
                                            _.get(
                                                datasource,
                                                "properties.connection.host",
                                                "-"
                                            ) +
                                            ":" +
                                            _.get(
                                                datasource,
                                                "properties.connection.port",
                                                "-"
                                            )}
                                    </Tag>
                                    <div
                                        className={classNames({
                                            "bp4-text-muted": true,
                                        })}
                                        style={{
                                            marginTop: 5,
                                            maxHeight: 80,
                                            lineHeight: "20px",
                                            overflow: "hidden",
                                        }}
                                    >
                                        {_.isEmpty(datasource.description)
                                            ? ""
                                            : datasource.description}
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
                                            border: "none",
                                        }}
                                    >
                                        <ButtonGroup large>
                                            <Popover
                                                {...BUTTON_WITH_TOOLTIP2}
                                                content="Edit"
                                            >
                                                <Button
                                                    onClick={(event) => {
                                                        event.stopPropagation();
                                                        setEditId(
                                                            datasource.id
                                                        );
                                                        setEntityName(
                                                            datasource.name
                                                        );
                                                    }}
                                                    intent={Intent.PRIMARY}
                                                    minimal
                                                    icon={<Icon icon="edit" />}
                                                />
                                            </Popover>
                                            <Popover
                                                {...BUTTON_WITH_TOOLTIP2}
                                                content="Delete"
                                            >
                                                <Button
                                                    onClick={(event) => {
                                                        event.stopPropagation();
                                                        setDeleteId(
                                                            datasource.id
                                                        );
                                                        setEntityName(
                                                            datasource.name
                                                        );
                                                    }}
                                                    intent={Intent.DANGER}
                                                    minimal
                                                    icon={<Icon icon="cross" />}
                                                />
                                            </Popover>
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
                                borderRadius: "40px",
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

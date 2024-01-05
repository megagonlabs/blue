import _ from "lodash";
import { useContext } from "react";
import { Col, Container, Row } from "react-grid-system";
import { AppContext } from "../app-context";
import RegistryCard from "./RegistryCard";
export default function RegistryList({ type }) {
    const { appState } = useContext(AppContext);
    return (
        <Container fluid>
            <Row gutterWidth={15} align="stretch" style={{ paddingTop: 14 }}>
                {_.get(appState, [type, "list"], []).map((element) => {
                    const properties = element.properties;
                    let extra = null;
                    switch (type) {
                        case "agent":
                            extra = properties.image;
                            break;
                        case "data":
                            extra = `${properties.connection.protocol}://${properties.connection.host}:${properties.connection.port}`;
                            break;
                    }
                    return (
                        <Col
                            key={`registry-list-${element.name}`}
                            sm={12}
                            md={6}
                            lg={4}
                            xxl={3}
                            style={{ paddingBottom: 15 }}
                        >
                            <RegistryCard
                                title={element.name}
                                description={element.description}
                                extra={extra}
                            />
                        </Col>
                    );
                })}
            </Row>
        </Container>
    );
}

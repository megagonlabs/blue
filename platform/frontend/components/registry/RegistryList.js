import { NonIdealState } from "@blueprintjs/core";
import _ from "lodash";
import { useRouter } from "next/router";
import { useContext } from "react";
import { Col, Container, Row } from "react-grid-system";
import { AppContext } from "../app-context";
import { REGISTRY_TYPE_LOOKUP } from "../constant";
import { faIcon } from "../icon";
import RegistryCard from "./RegistryCard";
export default function RegistryList({ type }) {
    const { appState } = useContext(AppContext);
    const list = _.get(appState, [type, "list"], []);
    const router = useRouter();
    if (_.isEmpty(list))
        return (
            <NonIdealState
                icon={faIcon({
                    icon: REGISTRY_TYPE_LOOKUP[type].icon,
                    size: 50,
                })}
                title={`No ${_.capitalize(type)}`}
            />
        );
    return (
        <Container fluid style={{ paddingLeft: 20, paddingRight: 20 }}>
            <Row gutterWidth={20} align="stretch" style={{ paddingTop: 10 }}>
                {list.map((element) => {
                    const properties = element.properties;
                    let extra = null,
                        key = type;
                    switch (type) {
                        case "agent":
                            extra = properties.image;
                            break;
                        case "data":
                            key = "source";
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
                            style={{ paddingBottom: 20 }}
                        >
                            <RegistryCard
                                title={element.name}
                                description={element.description}
                                extra={extra}
                                href={`${router.asPath}/${key}/${element.name}`}
                            />
                        </Col>
                    );
                })}
            </Row>
        </Container>
    );
}

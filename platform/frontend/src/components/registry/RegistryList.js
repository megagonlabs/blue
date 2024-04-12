import { AppContext } from "@/components/app-context";
import { REGISTRY_TYPE_LOOKUP } from "@/components/constant";
import { faIcon } from "@/components/icon";
import RegistryCard from "@/components/registry/RegistryCard";
import SearchList from "@/components/registry/SearchList";
import { Button, Card, Colors, Intent, NonIdealState } from "@blueprintjs/core";
import { faPlus } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext } from "react";
import { Col, Container, Row } from "react-grid-system";
export default function RegistryList({ type }) {
    const { appState } = useContext(AppContext);
    const list = appState[type].list;
    const router = useRouter();
    if (_.isEmpty(list))
        return (
            <NonIdealState
                icon={faIcon({
                    icon: REGISTRY_TYPE_LOOKUP[type].icon,
                    size: 50,
                })}
                title={`No ${_.capitalize(REGISTRY_TYPE_LOOKUP[type].key)}`}
                action={
                    _.includes(["agent"], type) ? (
                        <Link href={`${router.asPath}/new`}>
                            <Button
                                intent={Intent.PRIMARY}
                                large
                                outlined
                                icon={faIcon({ icon: faPlus })}
                                text={`Add ${REGISTRY_TYPE_LOOKUP[type].key}`}
                            />
                        </Link>
                    ) : null
                }
            />
        );
    if (appState[type].search) {
        return <SearchList type={type} />;
    }
    return (
        <Container fluid style={{ paddingLeft: 21, paddingRight: 21 }}>
            <Row gutterWidth={20} align="stretch" style={{ paddingTop: 1 }}>
                {list.map((element) => {
                    const properties = element.properties;
                    let extra = null,
                        key = REGISTRY_TYPE_LOOKUP[type].key;
                    _.if;
                    if (_.isEqual(type, "agent")) {
                        extra = properties.image;
                    } else if (_.isEqual(type, "data")) {
                        extra = `${properties.connection.protocol}://${properties.connection.host}:${properties.connection.port}`;
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
                {_.includes(["agent"], type) ? (
                    <Col
                        sm={12}
                        md={6}
                        lg={4}
                        xxl={3}
                        style={{ paddingBottom: 20 }}
                    >
                        <Link href={`${router.asPath}/new`}>
                            <Card
                                style={{
                                    minHeight: 127,
                                    padding: 0,
                                    height: "100%",
                                    position: "relative",
                                    backgroundColor: Colors.LIGHT_GRAY5,
                                    cursor: "pointer",
                                }}
                            >
                                <div
                                    style={{
                                        position: "absolute",
                                        top: "50%",
                                        left: "50%",
                                        textAlign: "center",
                                        transform: "translate(-50%, -50%)",
                                        msTransform: "translate(-50%, -50%)",
                                    }}
                                >
                                    <div style={{ marginBottom: 10 }}>
                                        {faIcon({ icon: faPlus, size: 20 })}
                                    </div>
                                    Add {type}
                                </div>
                            </Card>
                        </Link>
                    </Col>
                ) : null}
            </Row>
        </Container>
    );
}

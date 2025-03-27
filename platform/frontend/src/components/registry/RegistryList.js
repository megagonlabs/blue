import { ENTITY_TYPE_LOOKUP } from "@/components/constant";
import { AppContext } from "@/components/contexts/app-context";
import { AuthContext } from "@/components/contexts/auth-context";
import { faIcon } from "@/components/icon";
import RegistryCard from "@/components/registry/RegistryCard";
import SearchList from "@/components/registry/SearchList";
import {
    Button,
    Card,
    Classes,
    Intent,
    NonIdealState,
} from "@blueprintjs/core";
import { faPlusLarge } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext } from "react";
import { Col, Container, Row } from "react-grid-system";
import { populateRouterPathname } from "../helper";
export default function RegistryList({ type }) {
    const { appState } = useContext(AppContext);
    const list = appState[type].list;
    const loading = appState[type].loading;
    const router = useRouter();
    const { permissions } = useContext(AuthContext);
    const canAddEntity = (() => {
        if (_.isEqual(type, "agent") && permissions.canWriteAgentRegistry) {
            return true;
        } else if (
            _.isEqual(type, "data") &&
            permissions.canWriteDataRegistry
        ) {
            return true;
        } else if (
            _.isEqual(type, "operator") &&
            permissions.canWriteOperatorRegistry
        ) {
            return true;
        } else if (
            _.isEqual(type, "model") &&
            permissions.canWriteModelRegistry
        ) {
            return true;
        }
        return false;
    })();
    if (_.isEmpty(list))
        return (
            <div style={{ padding: "0px 20px 20px", height: "100%" }}>
                <NonIdealState
                    className={loading ? Classes.SKELETON : null}
                    icon={faIcon({
                        icon: ENTITY_TYPE_LOOKUP[type].icon,
                        size: 50,
                    })}
                    title={`No ${_.capitalize(ENTITY_TYPE_LOOKUP[type].key)}`}
                    action={
                        canAddEntity ? (
                            <Link
                                href={`${populateRouterPathname(router)}/new`}
                            >
                                <Button
                                    intent={Intent.PRIMARY}
                                    size="large"
                                    variant="outlined"
                                    icon={faIcon({ icon: faPlusLarge })}
                                    text={`Add ${ENTITY_TYPE_LOOKUP[type].key}`}
                                />
                            </Link>
                        ) : null
                    }
                />
            </div>
        );
    if (appState[type].search) {
        return <SearchList type={type} />;
    }
    return (
        <Container fluid style={{ paddingLeft: 21, paddingRight: 21 }}>
            <Row gutterWidth={20} align="stretch" style={{ paddingTop: 1 }}>
                {list.map((element) => {
                    const properties = element.properties;
                    let extra = null;
                    if (_.includes(["agent", "operator"], type)) {
                        extra = _.toString(properties.image);
                    } else if (_.isEqual(type, "data")) {
                        let protocol = _.get(properties, "connection.protocol");
                        let host = _.get(properties, "connection.host");
                        let port = _.get(properties, "connection.port");
                        if (!_.isEmpty(protocol)) extra = String(protocol);
                        if (!_.isEmpty(host)) extra += `://${host}`;
                        if (!_.isEmpty(port)) extra += `:${port}`;
                    }
                    let { icon } = element;
                    if (
                        !_.isEmpty(icon) &&
                        !_.startsWith(icon, "data:image/")
                    ) {
                        icon = _.split(icon, ":");
                    }
                    const displayName = _.get(
                        element,
                        "properties.display_name",
                        element.name
                    );
                    return (
                        <Col
                            key={element.name}
                            sm={12}
                            md={6}
                            lg={4}
                            xxl={3}
                            style={{ paddingBottom: 20 }}
                        >
                            <RegistryCard
                                type={type}
                                icon={icon}
                                title={displayName}
                                description={element.description}
                                properties={element.properties}
                                extra={extra}
                                href={`${populateRouterPathname(router)}/${
                                    element.name
                                }`}
                                container={element.container}
                            />
                        </Col>
                    );
                })}
                {canAddEntity ? (
                    <Col
                        sm={12}
                        md={6}
                        lg={4}
                        xxl={3}
                        style={{ paddingBottom: 20 }}
                    >
                        <Link
                            className="no-link-decoration"
                            href={`${populateRouterPathname(router)}/new`}
                        >
                            <Card
                                style={{
                                    minHeight: 127,
                                    padding: 0,
                                    height: "100%",
                                    position: "relative",
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
                                        {faIcon({
                                            icon: faPlusLarge,
                                            size: 20,
                                        })}
                                    </div>
                                    Add {ENTITY_TYPE_LOOKUP[type].key}
                                </div>
                            </Card>
                        </Link>
                    </Col>
                ) : null}
            </Row>
        </Container>
    );
}

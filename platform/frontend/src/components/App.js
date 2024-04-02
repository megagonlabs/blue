import {
    Alignment,
    Button,
    ButtonGroup,
    Card,
    H3,
    Intent,
    Navbar,
    NavbarHeading,
    Tag,
} from "@blueprintjs/core";
import {
    faCircleA,
    faCompassDrafting,
    faDatabase,
    faSignalStream,
} from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext } from "react";
import { AppContext } from "./app-context";
import { faIcon } from "./icon";
export default function App({ children }) {
    const router = useRouter();
    const { appState } = useContext(AppContext);
    const MENU_ITEMS = {
        sessions: { href: "/sessions", text: "Sessions", icon: faSignalStream },
        data: {
            href: `/data/${appState.data.registryName}`,
            text: "Data",
            icon: faDatabase,
        },
        agents: {
            href: `/agents/${appState.agent.registryName}`,
            text: "Agents",
            icon: faCircleA,
        },
        designer: {
            href: "/agents/designer",
            text: "Designer",
            icon: faCompassDrafting,
        },
    };
    return (
        <>
            <Navbar style={{ paddingLeft: 20, paddingRight: 20 }}>
                <Navbar.Group align="left">
                    <Image
                        width={25}
                        height={25}
                        src="/images/logo.png"
                        alt="Megagon Labs logo"
                    />
                    <Link href="/">
                        <NavbarHeading style={{ display: "flex" }}>
                            <H3 style={{ margin: "0px 10px 0px" }}>Blue</H3>
                            <Tag minimal intent={Intent.WARNING}>
                                Demo
                            </Tag>
                        </NavbarHeading>
                    </Link>
                </Navbar.Group>
            </Navbar>
            <Card
                interactive
                style={{
                    position: "absolute",
                    top: 50,
                    left: 0,
                    height: "calc(100vh - 50px)",
                    width: 160.55,
                    borderRadius: 0,
                    zIndex: 1,
                }}
            >
                <ButtonGroup alignText={Alignment.LEFT} vertical minimal large>
                    {["sessions", "data", "agents"].map((key, index) => {
                        const { href, icon, text } = _.get(MENU_ITEMS, key, {});
                        const active = _.startsWith(router.asPath, href);
                        return (
                            <Link
                                href={href}
                                key={`app-card-button-group-link-${index}`}
                            >
                                <Button
                                    style={
                                        !active
                                            ? { backgroundColor: "transparent" }
                                            : null
                                    }
                                    active={active}
                                    text={text}
                                    icon={faIcon({ icon: icon })}
                                />
                            </Link>
                        );
                    })}
                </ButtonGroup>
                <ButtonGroup
                    alignText={Alignment.LEFT}
                    vertical
                    minimal
                    large
                    style={{ marginTop: 20 }}
                >
                    {["designer"].map((key, index) => {
                        const { href, icon, text } = _.get(MENU_ITEMS, key, {});
                        const active = _.startsWith(router.asPath, href);
                        return (
                            <Link
                                href={href}
                                key={`app-card-button-group-link-${index}`}
                            >
                                <Button
                                    style={
                                        !active
                                            ? { backgroundColor: "transparent" }
                                            : null
                                    }
                                    active={active}
                                    text={text}
                                    icon={faIcon({ icon: icon })}
                                />
                            </Link>
                        );
                    })}
                </ButtonGroup>
            </Card>
            <div
                style={{
                    marginLeft: 160.55,
                    height: "calc(100vh - 50px)",
                    position: "relative",
                }}
            >
                {children}
            </div>
        </>
    );
}

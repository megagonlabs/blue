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
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import { useContext } from "react";
import { AppContext } from "./app-context";
import { faIcon } from "./icon";
export default function App({ children }) {
    const router = useRouter();
    const { appState } = useContext(AppContext);
    const MENU_ITEMS = [
        { href: "/sessions", text: "Sessions", icon: faSignalStream },
        {
            href: `/data/${appState.data.registryName}`,
            text: "Data",
            icon: faDatabase,
        },
        {
            href: `/agents/${appState.agent.registryName}`,
            text: "Agents",
            icon: faCircleA,
        },
    ];
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
                    {MENU_ITEMS.map(({ href, icon, text }, index) => {
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
                    style={{ marginTop: 40 }}
                >
                    <Link href="/designer">
                        <Button
                            style={
                                !_.startsWith(router.asPath, "/designer")
                                    ? { backgroundColor: "transparent" }
                                    : null
                            }
                            active={_.startsWith(router.asPath, "/designer")}
                            text="Designer"
                            icon={faIcon({ icon: faCompassDrafting })}
                        />
                    </Link>
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

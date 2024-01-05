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
    faDatabase,
    faSignalStream,
} from "@fortawesome/pro-duotone-svg-icons";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/router";
import { faIcon } from "./icon";
export default function App({ children }) {
    const router = useRouter();
    const MENU_ITEMS = [
        { href: "/sessions", text: "Sessions", icon: faSignalStream },
        { href: "/data", text: "Data", icon: faDatabase },
        { href: "/agents", text: "Agents", icon: faCircleA },
    ];
    return (
        <>
            <Navbar>
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
                style={{
                    position: "absolute",
                    top: 50,
                    left: 0,
                    height: "calc(100vh - 50px)",
                    width: 150.55,
                    padding: 15,
                    borderRadius: 0,
                    zIndex: 1,
                }}
            >
                <ButtonGroup alignText={Alignment.LEFT} vertical minimal large>
                    {MENU_ITEMS.map(({ href, icon, text }, index) => {
                        const active = _.isEqual(router.pathname, href);
                        return (
                            <Link
                                href={href}
                                key={`app-card-button_group-link-${index}`}
                            >
                                <Button
                                    intent={active ? Intent.PRIMARY : null}
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
                    marginLeft: 150.55,
                    height: "calc(100vh - 50px)",
                    position: "relative",
                }}
            >
                {children}
            </div>
        </>
    );
}

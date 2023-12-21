import {
    Card,
    H3,
    Menu,
    MenuItem,
    Navbar,
    NavbarHeading,
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
    return (
        <div>
            <Navbar>
                <Navbar.Group align="left">
                    <Image width={25} height={25} src="/images/logo.png" />
                    <Link href="/">
                        <NavbarHeading>
                            <H3 style={{ margin: 0, marginLeft: 10 }}>Blue</H3>
                        </NavbarHeading>
                    </Link>
                </Navbar.Group>
            </Navbar>
            <Card
                style={{
                    height: "calc(100vh - 50px)",
                    width: 210,
                    padding: 15,
                    borderRadius: 0,
                }}
            >
                <Menu large style={{ padding: 0 }}>
                    <Link href="/sessions">
                        <MenuItem
                            text="Sessions"
                            icon={faIcon({ icon: faSignalStream })}
                        />
                    </Link>
                    <MenuItem
                        disabled
                        text="Data"
                        icon={faIcon({ icon: faDatabase })}
                    />
                    <MenuItem
                        disabled
                        text="Agents"
                        icon={faIcon({ icon: faCircleA })}
                    />
                </Menu>
            </Card>
            <div>{children}</div>
        </div>
    );
}

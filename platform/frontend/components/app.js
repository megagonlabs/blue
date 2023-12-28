import {
    Alignment,
    Button,
    ButtonGroup,
    Card,
    H3,
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
                        <NavbarHeading>
                            <H3 style={{ margin: 0, marginLeft: 10 }}>Blue</H3>
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
                    <Link href="/sessions">
                        <Button
                            text="Sessions"
                            icon={faIcon({ icon: faSignalStream })}
                        />
                    </Link>
                    <Link href="/data">
                        <Button
                            disabled
                            text="Data"
                            icon={faIcon({ icon: faDatabase })}
                        />
                    </Link>
                    <Link href="/agents">
                        <Button
                            text="Agents"
                            icon={faIcon({ icon: faCircleA })}
                        />
                    </Link>
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

import { H3, Navbar } from "@blueprintjs/core";
export default function App({ children }) {
    return (
        <div>
            <Navbar>
                <Navbar.Group align="left">
                    <H3 style={{ margin: 0 }}>Blue</H3>
                </Navbar.Group>
            </Navbar>
            <div>{children}</div>
        </div>
    );
}

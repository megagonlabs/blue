import {
    Button,
    Card,
    Dialog,
    FormGroup,
    H4,
    InputGroup,
} from "@blueprintjs/core";
import _ from "lodash";
import { useContext, useState } from "react";
import { AppContext } from "../contexts/app-context";
export default function SessionDetail({ isOpen, setIsSessionDetailOpen }) {
    const { appState } = useContext(AppContext);
    const sessionIdFocus = appState.session.sessionIdFocus;
    const [tab, setTab] = useState("about");
    return (
        <Dialog
            style={{ padding: 20 }}
            onClose={() => {
                setIsSessionDetailOpen(false);
            }}
            isOpen={isOpen}
        >
            <H4>{sessionIdFocus}</H4>
            <Card style={{ padding: 5, marginBottom: 20 }}>
                <Button
                    minimal
                    text="About"
                    onClick={() => {
                        setTab("about");
                    }}
                    active={_.isEqual(tab, "about")}
                />
                <Button
                    minimal
                    text="Members"
                    onClick={() => {
                        setTab("members");
                    }}
                    active={_.isEqual(tab, "members")}
                />
            </Card>
            <FormGroup label="Name">
                <InputGroup
                    large
                    value={_.get(
                        appState,
                        ["session", "sessionDetail", sessionIdFocus, "name"],
                        ""
                    )}
                />
            </FormGroup>
            <FormGroup label="Description">
                <InputGroup
                    large
                    value={_.get(
                        appState,
                        [
                            "session",
                            "sessionDetail",
                            sessionIdFocus,
                            "description",
                        ],
                        ""
                    )}
                />
            </FormGroup>
        </Dialog>
    );
}

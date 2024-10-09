import { AuthContext } from "@/components/contexts/auth-context";
import { faIcon } from "@/components/icon";
import {
    Alignment,
    Button,
    Card,
    Classes,
    Colors,
    H1,
} from "@blueprintjs/core";
import {
    faMessageQuote,
    faPlus,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useContext } from "react";
export default function LaunchScreen() {
    const { user } = useContext(AuthContext);
    const name = _.get(user, "name", null);
    return (
        <div
            style={{
                margin: "auto",
                maxWidth: 600,
                marginTop: 100,
                padding: 20,
            }}
        >
            <H1 style={{ fontSize: 40, marginBottom: 10 }}>
                <label style={{ color: Colors.BLUE3 }}>Hello</label>
                {_.isEmpty(name) ? (
                    <label style={{ color: Colors.BLUE3 }}>.</label>
                ) : (
                    <>
                        <label style={{ color: Colors.BLUE3 }}>,</label>
                        &nbsp;
                        {name}.
                    </>
                )}
            </H1>
            <H1
                className={Classes.TEXT_MUTED}
                style={{ marginBottom: 60, fontSize: 40, opacity: 0.75 }}
            >
                How can I help you today&nbsp;
                {faIcon({
                    icon: faMessageQuote,
                    size: 43.5,
                })}
            </H1>
            <Card
                style={{
                    cursor: "pointer",
                    marginBottom: 20,
                    marginLeft: 1,
                    marginRight: 1,
                }}
            >
                agent group description
            </Card>
            <Button
                minimal
                alignText={Alignment.LEFT}
                fill
                large
                icon={faIcon({ icon: faPlus })}
                text="Add"
            />
        </div>
    );
}

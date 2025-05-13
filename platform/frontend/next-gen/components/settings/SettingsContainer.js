import { useAppStore } from "@/stores/app-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    CardList,
    Classes,
    Colors,
    EntityTitle,
    H3,
    Intent,
    Size,
    SwitchCard,
} from "@blueprintjs/core";
import {
    faMessages,
    faPaintRoller,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import { useShallow } from "zustand/react/shallow";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import { AppToaster } from "../toaster";
const SECTIONS = [
    { icon: faPaintRoller, text: "Appearance" },
    { icon: faMessages, text: "Sessions & Messages" },
];
const Subtext = ({ children }) => {
    return (
        <div className={classNames(Classes.TEXT_MUTED, Classes.TEXT_SMALL)}>
            {children}
        </div>
    );
};
function SettingsContainer({ width, height }) {
    const { darkMode, showWorkspace, expandMessage } = useAppStore(
        useShallow((state) => ({
            darkMode: state.dark_mode,
            showWorkspace: state.show_workspace,
            expandMessage: state.expand_message,
        }))
    );
    const setAppState = useAppStore((state) => state.setState);
    const saveSetting = ({ key, value }) => {
        setAppState({ key, value });
        axios.put(`/accounts/profile/settings/${key}`, { value }).then(() => {
            AppToaster.show({
                message: "Account settings updated",
                intent: Intent.SUCCESS,
            });
        });
    };
    return (
        <div style={{ width, height }}>
            <div className="full-parent-dimension" style={{ display: "flex" }}>
                <div
                    style={{
                        padding: 10,
                        overflowY: "auto",
                        minWidth: 235,
                    }}
                    className="border-right"
                >
                    <ButtonGroup
                        vertical
                        size={Size.LARGE}
                        alignText={Alignment.START}
                        variant={ButtonVariant.MINIMAL}
                    >
                        {SECTIONS.map((section) => (
                            <Button
                                icon={<FAIcon icon={section.icon} />}
                                text={section.text}
                            />
                        ))}
                    </ButtonGroup>
                </div>
                <div
                    className="full-parent-dimension"
                    style={{
                        backgroundColor: darkMode ? Colors.BLACK : null,
                        padding: 20,
                        overflowY: "auto",
                        overflowX: "hidden",
                    }}
                >
                    <div className="setting-container-section-1">
                        <div style={{ marginBottom: 10 }}>
                            <EntityTitle
                                icon={<FAIcon icon={faPaintRoller} size={20} />}
                                heading={H3}
                                title="Appearance"
                            />
                        </div>
                        <CardList className="overflow-hidden">
                            <SwitchCard
                                onChange={(event) => {
                                    saveSetting({
                                        key: "dark_mode",
                                        value: event.target.checked,
                                    });
                                }}
                                checked={darkMode}
                                compact
                                alignIndicator={Alignment.START}
                                showAsSelectedWhenChecked={false}
                            >
                                Dark mode
                                <Subtext>
                                    Change the color scheme from light to dark
                                </Subtext>
                            </SwitchCard>
                        </CardList>
                    </div>
                    <div
                        className="setting-container-section-2"
                        style={{ marginTop: 20 }}
                    >
                        <div style={{ marginBottom: 10 }}>
                            <EntityTitle
                                icon={<FAIcon icon={faMessages} size={20} />}
                                heading={H3}
                                title="Sessions & Messages"
                            />
                        </div>
                        <CardList className="overflow-hidden">
                            <SwitchCard
                                onChange={(event) => {
                                    saveSetting({
                                        key: "show_workspace",
                                        value: event.target.checked,
                                    });
                                }}
                                checked={showWorkspace}
                                compact
                                alignIndicator={Alignment.START}
                                showAsSelectedWhenChecked={false}
                            >
                                Show workspace
                                <Subtext>
                                    Default show session workspace
                                </Subtext>
                            </SwitchCard>
                            <SwitchCard
                                onChange={(event) => {
                                    saveSetting({
                                        key: "expand_message",
                                        value: event.target.checked,
                                    });
                                }}
                                checked={expandMessage}
                                compact
                                alignIndicator={Alignment.START}
                                showAsSelectedWhenChecked={false}
                            >
                                Expand message
                                <Subtext>
                                    Automatically expand session messages to
                                    show full content
                                </Subtext>
                            </SwitchCard>
                        </CardList>
                    </div>
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(SettingsContainer);

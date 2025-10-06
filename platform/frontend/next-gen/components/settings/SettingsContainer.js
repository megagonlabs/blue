import { scrollToTarget } from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import {
    Alignment,
    Button,
    ButtonGroup,
    ButtonVariant,
    Colors,
    Divider,
    EntityTitle,
    FormGroup,
    H3,
    Intent,
    Size,
    Switch,
} from "@blueprintjs/core";
import {
    faComments,
    faHistory,
    faPaintRoller,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import { useShallow } from "zustand/react/shallow";
import { useGridContainerContext } from "../contexts/GridContainerContext";
import { useToaster } from "../contexts/ToasterContext";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
import ResetSection from "./ResetSection";
const SECTIONS = [
    { icon: faPaintRoller, text: "Appearance" },
    { icon: faComments, text: "Sessions & Messages" },
    { icon: faHistory, text: "Reset" },
];
function SettingsContainer({ width, height }) {
    const {
        darkMode,
        showWorkspace,
        expandMessage,
        windowsControlButtons,
        detailedMessage,
        fullWindowHeight,
    } = useAppStore(
        useShallow((state) => ({
            darkMode: state.dark_mode,
            showWorkspace: state.show_workspace,
            expandMessage: state.expand_message,
            detailedMessage: state.detailed_message,
            windowsControlButtons: state.windows_control_buttons,
            fullWindowHeight: state.full_window_height,
        }))
    );
    const { gridContainerId } = useGridContainerContext();
    const setAppState = useAppStore((state) => state.setState);
    const { appToaster } = useToaster();
    const saveSetting = ({ key, value }) => {
        setAppState({ key, value });
        axios.put(`/accounts/profile/settings/${key}`, { value }).then(() => {
            appToaster.show({
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
                        {SECTIONS.map((section, index) => (
                            <Button
                                key={index}
                                icon={<FAIcon icon={section.icon} />}
                                text={section.text}
                                onClick={() => {
                                    const containerId = `container-${gridContainerId}`;
                                    const targetId = `container-${gridContainerId}-section-${index}`;
                                    scrollToTarget(containerId, targetId);
                                }}
                            />
                        ))}
                    </ButtonGroup>
                </div>
                <div
                    className="full-parent-dimension"
                    id={`container-${gridContainerId}`}
                    style={{
                        backgroundColor: darkMode ? Colors.BLACK : null,
                        padding: 20,
                        overflowY: "auto",
                        overflowX: "hidden",
                    }}
                >
                    <div id={`container-${gridContainerId}-section-0`}>
                        <EntityTitle
                            icon={<FAIcon icon={faPaintRoller} size={20} />}
                            heading={H3}
                            title="Appearance"
                        />
                        <Divider style={{ margin: "10px 0px 10px 0px" }} />
                        <div
                            style={{
                                borderRadius: 2,
                                padding: 15,
                                backgroundColor: darkMode
                                    ? Colors.DARK_GRAY2
                                    : Colors.LIGHT_GRAY5,
                            }}
                        >
                            <FormGroup
                                helperText={
                                    <div style={{ marginLeft: 45 }}>
                                        Change the color scheme from light to
                                        dark
                                    </div>
                                }
                                style={{ marginBottom: 10 }}
                            >
                                <Switch
                                    onChange={(event) => {
                                        saveSetting({
                                            key: "dark_mode",
                                            value: event.target.checked,
                                        });
                                    }}
                                    checked={darkMode}
                                    size={Size.LARGE}
                                    style={{ margin: "0px 0px 5px 0px" }}
                                    label="Dark mode"
                                />
                            </FormGroup>
                            <FormGroup
                                helperText={
                                    <div style={{ marginLeft: 45 }}>
                                        Relocate the window control buttons to
                                        the right side
                                    </div>
                                }
                                style={{ marginBottom: 10 }}
                            >
                                <Switch
                                    onChange={(event) => {
                                        saveSetting({
                                            key: "windows_control_buttons",
                                            value: event.target.checked,
                                        });
                                    }}
                                    checked={windowsControlButtons}
                                    size={Size.LARGE}
                                    style={{ margin: "0px 0px 5px 0px" }}
                                    label="Right-aligned window control buttons"
                                />
                            </FormGroup>
                            <FormGroup
                                helperText={
                                    <div style={{ marginLeft: 45 }}>
                                        New windows automatically expand to full
                                        height
                                    </div>
                                }
                                className="margin-0"
                            >
                                <Switch
                                    onChange={(event) => {
                                        saveSetting({
                                            key: "full_window_height",
                                            value: event.target.checked,
                                        });
                                    }}
                                    checked={fullWindowHeight}
                                    size={Size.LARGE}
                                    style={{ margin: "0px 0px 5px 0px" }}
                                    label="Full window height"
                                />
                            </FormGroup>
                        </div>
                    </div>
                    <div
                        id={`container-${gridContainerId}-section-1`}
                        style={{ marginTop: 20 }}
                    >
                        <EntityTitle
                            icon={<FAIcon icon={faComments} size={20} />}
                            heading={H3}
                            title="Sessions & Messages"
                        />
                        <Divider style={{ margin: "10px 0px 10px 0px" }} />
                        <div
                            style={{
                                borderRadius: 2,
                                padding: 15,
                                backgroundColor: darkMode
                                    ? Colors.DARK_GRAY2
                                    : Colors.LIGHT_GRAY5,
                            }}
                        >
                            <FormGroup
                                helperText={
                                    <div style={{ marginLeft: 45 }}>
                                        Default show session workspace
                                    </div>
                                }
                                style={{ marginBottom: 10 }}
                            >
                                <Switch
                                    onChange={(event) => {
                                        saveSetting({
                                            key: "show_workspace",
                                            value: event.target.checked,
                                        });
                                    }}
                                    checked={showWorkspace}
                                    size={Size.LARGE}
                                    style={{ margin: "0px 0px 5px 0px" }}
                                    label="Show workspace"
                                />
                            </FormGroup>
                            <FormGroup
                                helperText={
                                    <div style={{ marginLeft: 45 }}>
                                        Automatically expand session messages to
                                        show full content
                                    </div>
                                }
                                style={{ marginBottom: 10 }}
                            >
                                <Switch
                                    onChange={(event) => {
                                        saveSetting({
                                            key: "expand_message",
                                            value: event.target.checked,
                                        });
                                    }}
                                    checked={expandMessage}
                                    size={Size.LARGE}
                                    style={{ margin: "0px 0px 5px 0px" }}
                                    label="Expand messages"
                                />
                            </FormGroup>
                            <FormGroup
                                helperText={
                                    <div style={{ marginLeft: 45 }}>
                                        Display message details like timestamp,
                                        sender icon, and name
                                    </div>
                                }
                                className="margin-0"
                            >
                                <Switch
                                    checked={detailedMessage}
                                    onChange={(event) => {
                                        saveSetting({
                                            key: "detailed_message",
                                            value: event.target.checked,
                                        });
                                    }}
                                    size={Size.LARGE}
                                    style={{ margin: "0px 0px 5px 0px" }}
                                    label="Detailed messages"
                                />
                            </FormGroup>
                        </div>
                    </div>
                    <div
                        id={`container-${gridContainerId}-section-2`}
                        style={{ marginTop: 20 }}
                    >
                        <ResetSection />
                    </div>
                </div>
            </div>
        </div>
    );
}
export default withAutoSizer(SettingsContainer);

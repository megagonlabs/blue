import { AuthContext } from "@/components/contexts/auth-context";
import { faIcon } from "@/components/icon";
import {
    Classes,
    Drawer,
    DrawerSize,
    H3,
    Intent,
    Menu,
    MenuItem,
    Section,
    SectionCard,
    Switch,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowsFromLine,
    faBug,
    faCircleHalfStroke,
    faClipboard,
    faCode,
    faComments,
    faMessages,
    faPaintRoller,
    faSidebar,
    faTableColumns,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useContext } from "react";
import { AppToaster } from "../toaster";
const EXPLANATION_TEXT = {
    style: {
        marginTop: 5,
        whiteSpace: "initial",
        lineHeight: "initial",
    },
    className: classNames(Classes.TEXT_SMALL, Classes.TEXT_MUTED),
};
const SECTION_PROPS = {
    collapsible: true,
    collapseProps: { defaultIsOpen: false },
    compact: true,
};
const SESSION_MESSAGE_SETTINGS = {
    show_workspace: {
        title: "Show workspace",
        description: "Default show session workspace",
        icon: faTableColumns,
    },
    expand_message: {
        title: "Expand messages",
        description:
            "Automatically expand all session messages to show full content",
        icon: faArrowsFromLine,
    },
    conversation_view: {
        title: "Conversation view",
        description: "Whether messages should appear on opposite sides",
        icon: faComments,
    },
};
const APPEARANCE_SETTINGS = {
    dark_mode: {
        title: "Dark mode",
        description: "Change the color scheme from light to dark",
        icon: faCircleHalfStroke,
    },
    compact_sidebar: {
        title: "Compact sidebar",
        description: "Use minimal style for navigation menu",
        icon: faSidebar,
    },
};
const DEVELOPER_SETTINGS = {
    debug_mode: {
        title: "Debugger",
        description:
            "Show data inspection tool and other debugging information",
        icon: faBug,
    },
};
export default function Settings({ isOpen, setIsSettingsOpen }) {
    const { settings, updateSettings } = useContext(AuthContext);
    const darkMode = _.get(settings, "dark_mode", false);
    return (
        <Drawer
            className={darkMode ? Classes.DARK : null}
            size={DrawerSize.SMALL}
            isOpen={isOpen}
            onClose={() => setIsSettingsOpen(false)}
        >
            <div style={{ padding: 20, overflowY: "auto" }}>
                <div
                    style={{
                        marginBottom: 20,
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        gap: 40,
                    }}
                >
                    <H3 className="margin-0">Settings</H3>
                    <div style={{ maxWidth: "calc(100% - 123.71px)" }}>
                        <Tooltip
                            className="full-parent-width"
                            minimal
                            placement="bottom-end"
                            content={`Copy full SHA`}
                        >
                            <Tag
                                minimal
                                intent={Intent.PRIMARY}
                                interactive
                                onClick={() => {
                                    copy(process.env.NEXT_PUBLIC_GIT_LONG);
                                    AppToaster.show({
                                        icon: faIcon({ icon: faClipboard }),
                                        message: `Copied "${process.env.NEXT_PUBLIC_GIT_LONG}"`,
                                    });
                                }}
                            >
                                {process.env.NEXT_PUBLIC_GIT_BRANCH}-
                                {process.env.NEXT_PUBLIC_GIT_SHORT}
                            </Tag>
                        </Tooltip>
                    </div>
                </div>
                <Section
                    {...SECTION_PROPS}
                    icon={faIcon({ icon: faPaintRoller })}
                    title="Appearance"
                    style={{ marginBottom: 20 }}
                >
                    <SectionCard padded={false}>
                        <Menu
                            style={{ backgroundColor: "transparent" }}
                            className="settings-menus"
                            size="large"
                        >
                            {["dark_mode", "compact_sidebar"].map((key) => (
                                <MenuItem
                                    key={key}
                                    text={
                                        <div style={{ marginLeft: 3 }}>
                                            <div>
                                                {_.get(
                                                    APPEARANCE_SETTINGS,
                                                    [key, "title"],
                                                    "-"
                                                )}
                                            </div>
                                            <div {...EXPLANATION_TEXT}>
                                                {_.get(
                                                    APPEARANCE_SETTINGS,
                                                    [key, "description"],
                                                    "-"
                                                )}
                                            </div>
                                        </div>
                                    }
                                    icon={faIcon({
                                        icon: _.get(
                                            APPEARANCE_SETTINGS,
                                            [key, "icon"],
                                            null
                                        ),
                                    })}
                                    labelElement={
                                        <Switch
                                            checked={_.get(
                                                settings,
                                                key,
                                                false
                                            )}
                                            size="large"
                                            onChange={(event) =>
                                                updateSettings(
                                                    key,
                                                    event.target.checked
                                                )
                                            }
                                        />
                                    }
                                />
                            ))}
                        </Menu>
                    </SectionCard>
                </Section>
                <Section
                    {...SECTION_PROPS}
                    icon={faIcon({ icon: faMessages })}
                    title="Sessions & Messages"
                    style={{ marginBottom: 20 }}
                >
                    <SectionCard padded={false}>
                        <Menu
                            style={{ backgroundColor: "transparent" }}
                            className="settings-menus"
                            size="large"
                        >
                            {[
                                "show_workspace",
                                "expand_message",
                                "conversation_view",
                            ].map((key) => (
                                <MenuItem
                                    key={key}
                                    text={
                                        <div style={{ marginLeft: 3 }}>
                                            <div>
                                                {_.get(
                                                    SESSION_MESSAGE_SETTINGS,
                                                    [key, "title"],
                                                    "-"
                                                )}
                                            </div>
                                            <div {...EXPLANATION_TEXT}>
                                                {_.get(
                                                    SESSION_MESSAGE_SETTINGS,
                                                    [key, "description"],
                                                    "-"
                                                )}
                                            </div>
                                        </div>
                                    }
                                    icon={faIcon({
                                        icon: _.get(
                                            SESSION_MESSAGE_SETTINGS,
                                            [key, "icon"],
                                            null
                                        ),
                                    })}
                                    labelElement={
                                        <Switch
                                            checked={_.get(
                                                settings,
                                                key,
                                                false
                                            )}
                                            style={{ marginBottom: 0 }}
                                            size="large"
                                            onChange={(event) => {
                                                updateSettings(
                                                    key,
                                                    event.target.checked
                                                );
                                            }}
                                        />
                                    }
                                />
                            ))}
                        </Menu>
                    </SectionCard>
                </Section>
                <Section
                    {...SECTION_PROPS}
                    icon={faIcon({ icon: faCode })}
                    title="Developer"
                >
                    <SectionCard padded={false}>
                        <Menu
                            style={{ backgroundColor: "transparent" }}
                            className="settings-menus"
                            size="large"
                        >
                            {["debug_mode"].map((key) => (
                                <MenuItem
                                    key={key}
                                    text={
                                        <div style={{ marginLeft: 3 }}>
                                            <div>
                                                {_.get(
                                                    DEVELOPER_SETTINGS,
                                                    [key, "title"],
                                                    "-"
                                                )}
                                            </div>
                                            <div {...EXPLANATION_TEXT}>
                                                {_.get(
                                                    DEVELOPER_SETTINGS,
                                                    [key, "description"],
                                                    "-"
                                                )}
                                            </div>
                                        </div>
                                    }
                                    icon={faIcon({
                                        icon: _.get(
                                            DEVELOPER_SETTINGS,
                                            [key, "icon"],
                                            null
                                        ),
                                    })}
                                    labelElement={
                                        <Switch
                                            checked={_.get(
                                                settings,
                                                key,
                                                false
                                            )}
                                            style={{ marginBottom: 0 }}
                                            size="large"
                                            onChange={(event) => {
                                                updateSettings(
                                                    key,
                                                    event.target.checked
                                                );
                                            }}
                                        />
                                    }
                                />
                            ))}
                        </Menu>
                    </SectionCard>
                </Section>
            </div>
        </Drawer>
    );
}

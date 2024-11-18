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
    faClipboard,
    faCode,
    faMessages,
    faPaintRoller,
    faSidebar,
    faTableColumns,
    faTableList,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import classNames from "classnames";
import copy from "copy-to-clipboard";
import _ from "lodash";
import { useContext } from "react";
import { AuthContext } from "../contexts/auth-context";
import { faIcon } from "../icon";
import { AppToaster } from "../toaster";
export default function Settings({ isOpen, setIsSettingsOpen }) {
    const { settings, updateSettings } = useContext(AuthContext);
    const SECTION_PROPS = {
        collapsible: true,
        collapseProps: { defaultIsOpen: false },
        compact: true,
    };
    const EXPLANATION_TEXT = {
        style: {
            marginTop: 5,
            whiteSpace: "initial",
            lineHeight: "initial",
        },
        className: classNames(Classes.TEXT_SMALL, Classes.TEXT_MUTED),
    };
    const SESSION_MESSAGE_SETTINGS = {
        show_workspace: {
            title: "Show workspace",
            description: "Default show session workspace",
            icon: faTableColumns,
        },
        show_session_list: {
            title: "Show sessions",
            description: "Default show session categorization list",
            icon: faTableList,
        },
        expand_message: {
            title: "Expand messages",
            description:
                "Automatically expand all session messages to show full content",
            icon: faArrowsFromLine,
        },
    };
    const APPEARANCE_SETTINGS = {
        compact_sidebar: {
            title: "Compact sidebar",
            description: "Use minimal style for vavigation menu",
            icon: faSidebar,
        },
    };
    return (
        <Drawer
            size={DrawerSize.SMALL}
            isOpen={isOpen}
            onClose={() => {
                setIsSettingsOpen(false);
            }}
        >
            <div style={{ padding: 20 }}>
                <div
                    style={{
                        marginBottom: 20,
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        gap: 10,
                    }}
                >
                    <H3 className="margin-0">Settings</H3>
                    <Tooltip
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
                <Section
                    {...SECTION_PROPS}
                    icon={faIcon({ icon: faPaintRoller })}
                    title="Appearance"
                    style={{ marginBottom: 15 }}
                >
                    <SectionCard padded={false}>
                        <Menu className="settings-menus" large>
                            {["compact_sidebar"].map((key) => (
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
                                            style={{ marginBottom: 0 }}
                                            large
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
                    icon={faIcon({ icon: faMessages })}
                    title="Sessions & Messages"
                    style={{ marginBottom: 15 }}
                >
                    <SectionCard padded={false}>
                        <Menu className="settings-menus" large>
                            {[
                                "show_workspace",
                                "show_session_list",
                                "expand_message",
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
                                            large
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
                        <Menu className="settings-menus" large>
                            <MenuItem
                                text={
                                    <div style={{ marginLeft: 3 }}>
                                        <div>Debug mode</div>
                                        <div {...EXPLANATION_TEXT}>
                                            Show data inspection tool and other
                                            debugging information
                                        </div>
                                    </div>
                                }
                                icon={faIcon({ icon: faBug })}
                                labelElement={
                                    <Switch
                                        checked={_.get(
                                            settings,
                                            "debug_mode",
                                            false
                                        )}
                                        style={{ marginBottom: 0 }}
                                        large
                                        onChange={(event) => {
                                            updateSettings(
                                                "debug_mode",
                                                event.target.checked
                                            );
                                        }}
                                    />
                                }
                            />
                        </Menu>
                    </SectionCard>
                </Section>
            </div>
        </Drawer>
    );
}

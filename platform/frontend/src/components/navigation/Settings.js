import {
    Classes,
    Drawer,
    DrawerSize,
    H3,
    Menu,
    MenuItem,
    Section,
    SectionCard,
    Switch,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowsFromDottedLine,
    faCode,
    faMessages,
    faRectangleTerminal,
} from "@fortawesome/pro-duotone-svg-icons";
import classNames from "classnames";
import _ from "lodash";
import { useContext } from "react";
import { AuthContext } from "../contexts/auth-context";
import { faIcon } from "../icon";
export default function Settings({ isOpen, setIsSettingsOpen }) {
    const { settings, updateSettings } = useContext(AuthContext);
    const SECTION_PROPS = {
        collapsible: true,
        collapseProps: { defaultIsOpen: false },
        compact: true,
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
                        alignItems: "center",
                        gap: 10,
                    }}
                >
                    <H3 className="margin-0">Settings</H3>
                    <Tooltip
                        placement="bottom"
                        content={process.env.NEXT_PUBLIC_GIT_LONG}
                    >
                        <Tag minimal>
                            {process.env.NEXT_PUBLIC_GIT_BRANCH}-
                            {process.env.NEXT_PUBLIC_GIT_SHORT}
                        </Tag>
                    </Tooltip>
                </div>
                <Section
                    {...SECTION_PROPS}
                    icon={faIcon({ icon: faMessages })}
                    title="Messages"
                    style={{ marginBottom: 10 }}
                >
                    <SectionCard padded={false}>
                        <Menu className="settings-menus" large>
                            <MenuItem
                                text={
                                    <div style={{ marginLeft: 3 }}>
                                        <div>Expand to show more</div>
                                        <div
                                            className={classNames(
                                                Classes.TEXT_SMALL,
                                                Classes.TEXT_MUTED
                                            )}
                                        >
                                            Always expand all messages
                                        </div>
                                    </div>
                                }
                                icon={faIcon({ icon: faArrowsFromDottedLine })}
                                labelElement={
                                    <Switch
                                        checked={_.get(
                                            settings,
                                            "expand_message",
                                            false
                                        )}
                                        style={{ marginBottom: 0 }}
                                        large
                                        onChange={(event) => {
                                            updateSettings(
                                                "expand_message",
                                                event.target.checked
                                            );
                                        }}
                                    />
                                }
                            />
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
                                        <div
                                            className={classNames(
                                                Classes.TEXT_SMALL,
                                                Classes.TEXT_MUTED
                                            )}
                                        >
                                            Show debugger window
                                        </div>
                                    </div>
                                }
                                icon={faIcon({ icon: faRectangleTerminal })}
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

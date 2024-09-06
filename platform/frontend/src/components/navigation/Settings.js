import {
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
import { faRectangleTerminal } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useContext } from "react";
import { AuthContext } from "../contexts/auth-context";
import { faIcon } from "../icon";
export default function Settings({ isOpen, setIsSettingsOpen }) {
    const { settings, updateSettings } = useContext(AuthContext);
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
                <Section compact title="Developer">
                    <SectionCard padded={false}>
                        <Menu className="settings-menus" large>
                            <MenuItem
                                text="Debug mode"
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

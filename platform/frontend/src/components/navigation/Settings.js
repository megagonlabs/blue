import { Drawer, DrawerSize, H3, Tag, Tooltip } from "@blueprintjs/core";
export default function Settings({ isOpen, setIsSettingsOpen }) {
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
            </div>
        </Drawer>
    );
}

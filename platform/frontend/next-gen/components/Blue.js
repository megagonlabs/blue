import { Card, Menu, MenuDivider, MenuItem } from "@blueprintjs/core";
import Image from "next/image";
import ExpandingBox from "./ExpandingBox";

export default function Blue({ children }) {
    return (
        <div style={{ height: "100vh", width: "100vw" }}>
            <div style={{ position: "absolute", top: 20, left: 20 }}>
                <ExpandingBox
                    initialWidth={65}
                    initialHeight={65}
                    expandedWidth={250}
                    expandedHeight={590}
                >
                    {(isExpanded) => (
                        <Card
                            interactive
                            style={{
                                width: "100%",
                                height: "100%",
                                overflow: isExpanded ? "auto" : "hidden",
                            }}
                        >
                            <Image
                                width={25}
                                height={25}
                                src="/images/logo.png"
                                alt="Megagon Labs logo"
                            />
                            {isExpanded && (
                                <div style={{ marginTop: 10 }}>
                                    <Menu>
                                        <MenuDivider title="Sessions" />
                                        <MenuItem text="All Sessions" />
                                        <MenuItem text="New Session" />
                                        <MenuDivider title="Registries" />
                                        <MenuItem text="Agent" />
                                        <MenuItem text="Data" />
                                        <MenuItem text="Operator" />
                                        <MenuItem text="Model" />
                                        <MenuDivider title="Tools" />
                                        <MenuItem text="Form Designer" />
                                        <MenuDivider title="Administrator" />
                                        <MenuItem text="System Status" />
                                        <MenuItem text="Agents" />
                                        <MenuItem text="Services" />
                                        <MenuItem text="Users" />
                                        <MenuItem text="Configurations" />
                                    </Menu>
                                </div>
                            )}
                        </Card>
                    )}
                </ExpandingBox>
            </div>
            {children}
        </div>
    );
}

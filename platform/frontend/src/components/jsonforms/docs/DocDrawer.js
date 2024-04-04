import { Drawer, DrawerSize, Position } from "@blueprintjs/core";
export default function DocDrawer({ isOpen, setIsDocOpen }) {
    return (
        <Drawer
            isOpen={isOpen}
            hasBackdrop={false}
            enforceFocus={false}
            autoFocus
            canOutsideClickClose={false}
            canEscapeKeyClose
            position={Position.RIGHT}
            onClose={() => {
                setIsDocOpen(false);
            }}
            size={DrawerSize.STANDARD}
        ></Drawer>
    );
}

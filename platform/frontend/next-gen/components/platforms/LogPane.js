import { useAppStore } from "@/stores/app-store";
import { Colors } from "@blueprintjs/core";
import { motion } from "framer-motion";
import AgentLogs from "./AgentLogs";
export default function LogPane({
    show,
    setShow,
    containerId,
    setContainerId,
}) {
    const darkMode = useAppStore((state) => state.dark_mode);
    const variants = {
        open: {
            x: 0,
            display: "block",
            transition: { duration: 0.15 },
        },
        closed: {
            x: 200,
            transition: { duration: 0.15 },
            display: "none",
        },
        initial: { x: 200, opacity: 1, display: "none" },
    };
    return (
        <motion.div
            variants={variants}
            initial="initial"
            animate={show ? "open" : "closed"}
            className="full-parent-height border-left border-raidus-20"
            style={{
                position: "fixed",
                maxHeight: "calc(100% - 45px)",
                top: 45,
                right: 0,
                zIndex: 10,
                width: "calc(100% + 1px)",
                maxWidth: "min(calc(100% + 1px), 600px)",
                backgroundColor: darkMode ? Colors.BLACK : Colors.WHITE,
                overflowY: "auto",
            }}
        >
            <AgentLogs
                leftBoundary={true}
                containerId={containerId}
                setContainerId={setContainerId}
                setShow={setShow}
            />
        </motion.div>
    );
}

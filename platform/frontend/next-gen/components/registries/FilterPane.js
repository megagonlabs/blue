import { useAppStore } from "@/stores/app-store";
import {
    Button,
    ButtonVariant,
    Classes,
    Colors,
    Size,
} from "@blueprintjs/core";
import { faArrowLeft } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { motion } from "framer-motion";
import { FAIcon } from "../FAIcon";
export default function FilterPane({ showFilter, setShowFilter, children }) {
    const darkMode = useAppStore((state) => state.darkMode);
    const variants = {
        open: {
            x: 0,
            display: "block",
            transition: { duration: 0.15 },
        },
        closed: {
            x: -200,
            transition: { duration: 0.15 },
            display: "none",
        },
        initial: { x: -200, opacity: 1, display: "none" },
    };
    return (
        <motion.div
            variants={variants}
            initial="initial"
            animate={showFilter ? "open" : "closed"}
            className="full-parent-height border-right border-raidus-20"
            style={{
                position: "fixed",
                maxHeight: "calc(100% - 45px)",
                top: 45,
                left: 0,
                zIndex: 1,
                padding: 20,
                width: 200,
                backgroundColor: darkMode ? Colors.DARK_GRAY2 : Colors.WHITE,
                overflowY: "auto",
            }}
        >
            <div
                className={Classes.TEXT_LARGE}
                style={{
                    lineHeight: "40px",
                    fontWeight: 600,
                    marginBottom: 20,
                }}
            >
                Filter
            </div>
            <Button
                style={{ position: "absolute", top: 20, right: 20 }}
                icon={<FAIcon icon={faArrowLeft} />}
                size={Size.LARGE}
                variant={ButtonVariant.MINIMAL}
                onClick={() => {
                    setShowFilter(false);
                }}
            />
            {children}
        </motion.div>
    );
}

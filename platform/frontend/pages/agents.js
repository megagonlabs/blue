import AgentList from "@/components/agents/AgentList";
import { H4 } from "@blueprintjs/core";
import { useEffect } from "react";
export default function Agents() {
    useEffect(() => {}, []);
    return (
        <>
            <div
                style={{
                    // position: "absolute",
                    top: 20,
                    left: 20,
                    height: "100%",
                    width: "100%",
                }}
            >
                <H4
                    className="margin-0"
                    style={{
                        lineHeight: "30px",
                        marginRight: 10,
                    }}
                >
                    Agents Registry (default)
                </H4>
                <AgentList />
            </div>
        </>
    );
}

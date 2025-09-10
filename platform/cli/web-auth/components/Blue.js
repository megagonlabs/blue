import { Intent, Spinner } from "@blueprintjs/core";
import { useToaster } from "./contexts/ToasterContext";
export default function Blue({ children }) {
    const { initialized } = useToaster();
    if (!initialized) {
        return (
            <div className="center-center">
                <Spinner intent={Intent.PRIMARY} />
            </div>
        );
    }
    return children;
}

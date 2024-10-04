import { NonIdealState } from "@blueprintjs/core";
import { faRoadBarrier } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useRouter } from "next/router";
import { faIcon } from "./icon";
export default function AccessDeniedNonIdealState() {
    const router = useRouter();
    return (
        <NonIdealState
            title="No Permission"
            description="Sorry, but you don't have permission to access this page"
            icon={faIcon({ icon: faRoadBarrier, size: 50 })}
            action={
                <div>
                    You can go back to&nbsp;
                    <a
                        style={{ fontWeight: 600, cursor: "pointer" }}
                        onClick={() => {
                            router.back();
                        }}
                    >
                        previous page
                    </a>
                </div>
            }
        />
    );
}

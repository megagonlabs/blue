import { FAIcon } from "@/components/FAIcon";
import { Button, NonIdealState, Size } from "@blueprintjs/core";
import { faPersonDigging } from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useRouter } from "next/router";
export default function Custom404() {
    const router = useRouter();
    const handleClick = () => {
        router.push("/");
    };
    return (
        <NonIdealState
            title="404 That's an error"
            description="The requested URL is not valid."
            icon={<FAIcon size={50} icon={faPersonDigging} />}
            action={
                <Button
                    size={Size.LARGE}
                    text="Go Back"
                    onClick={handleClick}
                />
            }
        />
    );
}

import { useUIVisibilityStore } from "@/stores/ui-visibility-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Checkbox,
    Classes,
    Intent,
    Popover,
    Size,
    Tooltip,
} from "@blueprintjs/core";
import { faFlag } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useEffect } from "react";
import { useShallow } from "zustand/react/shallow";
import { useTour } from "../contexts/TourContext";
import { FAIcon } from "../FAIcon";
import { AppToaster } from "../toaster";
export default function UITour() {
    const { startTour } = useTour();
    const id = "platform-onboarding-tour";
    const { UIVisibility, setVisibility, queue } = useUIVisibilityStore(
        useShallow((state) => ({
            UIVisibility: state.UIVisibility,
            setVisibility: state.setVisibility,
            queue: state.queue,
        }))
    );
    const onChange = (event) => {
        setVisibility({ id, value: !event.target.checked });
    };
    useEffect(() => {
        if (_.get(UIVisibility, id, true)) {
            AppToaster.show({
                timeout: 10000,
                intent: Intent.PRIMARY,
                icon: <FAIcon icon={faFlag} />,
                message:
                    "To start a basic tour, select the flag in the top-left corner.",
            });
        }
    }, []);
    if (!_.get(UIVisibility, id, true)) {
        return null;
    }
    return (
        <ButtonGroup fill style={{ marginBottom: 20 }}>
            <Popover
                placement="right"
                content={
                    <div style={{ padding: 10 }}>
                        <Button
                            fill
                            className={Classes.POPOVER_DISMISS}
                            size={Size.LARGE}
                            onClick={startTour}
                            text="Start the tour"
                            intent={Intent.PRIMARY}
                        />
                        <Checkbox
                            className={
                                _.get(queue, id, false) && Classes.SKELETON
                            }
                            onChange={onChange}
                            checked={!_.get(UIVisibility, id, true)}
                            style={{
                                marginBottom: 0,
                                marginTop: 10,
                            }}
                            label="Don't show this again"
                        />
                    </div>
                }
            >
                <Tooltip content="Tour" openOnTargetFocus={false}>
                    <Button
                        icon={<FAIcon icon={faFlag} />}
                        variant={ButtonVariant.MINIMAL}
                    />
                </Tooltip>
            </Popover>
        </ButtonGroup>
    );
}

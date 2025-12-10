import { settlePromises } from "@/components/helper";
import { useAppStore } from "@/stores/app-store";
import { useUIVisibilityStore } from "@/stores/ui-visibility-store";
import {
    Button,
    ButtonVariant,
    Colors,
    Divider,
    EntityTitle,
    FormGroup,
    H3,
    Intent,
    Size,
} from "@blueprintjs/core";
import { faHistory } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import _ from "lodash";
import { useState } from "react";
import { useShallow } from "zustand/react/shallow";
import { useToaster } from "../contexts/ToasterContext";
import { FAIcon } from "../FAIcon";
export default function ResetSection() {
    const { darkMode } = useAppStore(
        useShallow((state) => ({ darkMode: state.dark_mode }))
    );
    const [visibilityReset, setVisibilityReset] = useState(false);
    const { setState: setUIVisibility } = useUIVisibilityStore(
        useShallow((state) => ({ setState: state.setState }))
    );
    const { appToaster, progressToaster, showAxiosErrorToast } = useToaster();
    const onVisibilityReset = () => {
        setVisibilityReset(true);
        const ids = [
            "session_inspection_debugger",
            "debugger_stream_flows_nodes",
            "window_control_bar_maximization_tip",
            "derived_agents_configurations_override",
            "data_registry_source_entity_synchronize",
            "card_list_double_right_click_callout",
            "platform_onboarding_tour",
        ];
        let promises = [];
        for (let i = 0; i < _.size(ids); i++) {
            promises.push(
                new Promise((resolve, reject) => {
                    axios
                        .put(`/accounts/profile/ui_visibility/${ids[i]}`, {
                            value: true,
                        })
                        .then(() => {
                            resolve();
                        })
                        .catch((error) => {
                            showAxiosErrorToast(error);
                            reject();
                        });
                })
            );
        }
        settlePromises(
            promises,
            ({ error }) => {
                if (!error) {
                    appToaster.show({
                        message: "Tour and tips are now all visible",
                        intent: Intent.SUCCESS,
                    });
                }
                setVisibilityReset(false);
                axios.get("/accounts/profile").then((response) => {
                    const user = _.get(response, "data.profile", null);
                    setUIVisibility({
                        key: "UIVisibility",
                        value: _.get(user, "ui_visibility", {}),
                    });
                });
            },
            progressToaster
        );
    };
    return (
        <>
            <EntityTitle
                icon={<FAIcon icon={faHistory} size={20} />}
                heading={H3}
                title="Reset"
            />
            <Divider style={{ margin: "10px 0px 10px 0px" }} />
            <div
                style={{
                    borderRadius: 2,
                    padding: 20,
                    backgroundColor: darkMode
                        ? Colors.DARK_GRAY2
                        : Colors.LIGHT_GRAY5,
                }}
            >
                <FormGroup
                    className="margin-0"
                    subLabel="Reset visibilities of all tour and tips"
                    label="Tour & Tip Visibility"
                >
                    <Button
                        loading={visibilityReset}
                        size={Size.LARGE}
                        variant={ButtonVariant.MINIMAL}
                        intent={Intent.DANGER}
                        text="Reset"
                        onClick={onVisibilityReset}
                    />
                </FormGroup>
            </div>
        </>
    );
}

import { FAIcon } from "@/components/FAIcon";
import SessionContainer from "@/components/sessions/SessionContainer";
import SessionDisplayName from "@/components/sessions/SessionDisplayName";
import { useAuthStore } from "@/stores/auth-store";
import { useGridStore } from "@/stores/grid-layout-store";
import { useSessionStore } from "@/stores/session-store";
import {
    Button,
    ButtonGroup,
    ButtonVariant,
    Intent,
    Size,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    fa1,
    fa2,
    fa3,
    fa4,
    fa5,
    faComments,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import { useEffect, useMemo } from "react";
import { useShallow } from "zustand/react/shallow";
const NUMBER_TO_ICON = {
    1: fa1,
    2: fa2,
    3: fa3,
    4: fa4,
    5: fa5,
};
export default function TopSessions() {
    const user = useAuthStore((state) => state.user);
    const { sessionIds, getSessions, sessions } = useSessionStore(
        useShallow((state) => ({
            getSessions: state.getSessions,
            sessionIds: state.sessionIds,
            sessions: state.sessions,
        }))
    );
    useEffect(() => {
        getSessions();
    }, []);
    const topSessions = useMemo(() => {
        let result = sessionIds
            .filter((id) => {
                return _.isEqual(
                    _.get(sessions, [id, "details", "created_by"], null),
                    user.uid
                );
            })
            .sort((left, right) => {
                return (
                    _.get(sessions, [right, "details", "created_date"]) -
                    _.get(sessions, [left, "details", "created_date"])
                );
            });
        return result.slice(0, 5);
    }, [sessionIds, sessions, user]);
    const { layout, addContainer } = useGridStore(
        useShallow((state) => ({
            layout: state.layout,
            addContainer: state.addContainer,
        }))
    );
    if (_.isEmpty(topSessions)) {
        return null;
    }
    return (
        <div
            className="full-parent-width border-bottom"
            style={{
                padding: "10px 0px",
                overflow: "hidden",
                position: "relative",
                marginBottom: 20,
            }}
        >
            <Tag
                minimal
                intent={Intent.PRIMARY}
                style={{
                    top: 0,
                    left: 0,
                    width: 65,
                    position: "absolute",
                    textAlign: "center",
                }}
                fill
            >
                Sessions
            </Tag>
            <div style={{ height: "calc(100% - 20px)", marginTop: 20 }}>
                <ButtonGroup
                    vertical
                    size={Size.LARGE}
                    variant={ButtonVariant.MINIMAL}
                    fill
                >
                    {topSessions.map((sessionId, index) => (
                        <Tooltip
                            key={index}
                            content={
                                <SessionDisplayName sessionId={sessionId} />
                            }
                        >
                            <Button
                                icon={
                                    <FAIcon icon={NUMBER_TO_ICON[index + 1]} />
                                }
                                onClick={() => {
                                    addContainer({
                                        icon: faComments,
                                        title: (
                                            <SessionDisplayName
                                                sessionId={sessionId}
                                            />
                                        ),
                                        content: (
                                            <SessionContainer
                                                sessionId={sessionId}
                                            />
                                        ),
                                    });
                                }}
                            />
                        </Tooltip>
                    ))}
                </ButtonGroup>
            </div>
        </div>
    );
}

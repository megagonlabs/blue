import EntityDescription from "@/components/entity/EntityDescription";
import EntityProperties from "@/components/entity/EntityProperties";
import { faIcon } from "@/components/icon";
import {
    Button,
    Classes,
    EditableText,
    Intent,
    Section,
    SectionCard,
} from "@blueprintjs/core";
import { faCheck } from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useSearchParams } from "next/navigation";
import { useRouter } from "next/router";
import { useEffect } from "react";
export default function NewEntity({
    type,
    entity,
    updateEntity,
    saveEntity,
    loading,
    jsonError,
    setJsonError,
    setLoading,
    urlPrefix,
    setEntity,
}) {
    const router = useRouter();
    const searchParams = useSearchParams();
    useEffect(() => {
        if (!router.isReady) return;
        const entity = searchParams.get("entity");
        if (_.isEmpty(entity)) return;
        axios.get(`${urlPrefix}/${entity}`).then((response) => {
            let result = _.get(response, "data.result", {});
            _.set(result, "name", "");
            if (!_.isEmpty(result)) {
                setEntity(_.get(response, "data.result", {}));
            }
        });
    }, [router]);
    return (
        <div style={{ padding: "10px 20px 20px" }}>
            <Section compact style={{ position: "relative" }}>
                <SectionCard padded={false}>
                    <div style={{ display: "flex" }}>
                        <div
                            className={classNames(
                                Classes.TEXT_MUTED,
                                "required"
                            )}
                            style={{ width: 52.7, margin: "20px 0px 0px 20px" }}
                        >
                            Name
                        </div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{
                                width: "calc(100% - 248.86px)",
                                padding: "20px 10px 10px 10px",
                            }}
                        >
                            <EditableText
                                intent={
                                    _.isEmpty(entity.name)
                                        ? Intent.DANGER
                                        : null
                                }
                                value={entity.name}
                                onChange={(value) => {
                                    updateEntity({ path: "name", value });
                                }}
                            />
                        </div>
                    </div>
                    <div style={{ display: "flex" }}>
                        <div
                            className={Classes.TEXT_MUTED}
                            style={{ width: 52.7, margin: "0px 0px 20px 20px" }}
                        >
                            Type
                        </div>
                        <div
                            className={Classes.TEXT_OVERFLOW_ELLIPSIS}
                            style={{
                                width: "calc(100% - 248.86px)",
                                padding: "0px 10px 20px 10px",
                            }}
                        >
                            {type}
                        </div>
                    </div>
                    <div
                        style={{
                            position: "absolute",
                            right: 15,
                            top: "50%",
                            transform: "translateY(-50%)",
                            msTransform: "translateY(-50%)",
                        }}
                    >
                        <Button
                            className={loading ? Classes.SKELETON : null}
                            large
                            disabled={jsonError || _.isEmpty(entity.name)}
                            intent={Intent.SUCCESS}
                            text="Save"
                            onClick={saveEntity}
                            icon={faIcon({ icon: faCheck })}
                        />
                    </div>
                </SectionCard>
            </Section>
            <EntityDescription
                edit
                entity={entity}
                updateEntity={updateEntity}
            />
            <EntityProperties
                edit
                entity={entity}
                jsonError={jsonError}
                setJsonError={setJsonError}
                updateEntity={updateEntity}
                setLoading={setLoading}
            />
        </div>
    );
}

import { faIcon } from "@/components/icon";
import JsonForm from "@/components/sessions/message/renderers/JsonForm";
import JsonViewer from "@/components/sessions/message/renderers/JsonViewer";
import { Tag } from "@blueprintjs/core";
import { faPenLine } from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
export default function MessageContent({
    isDragPreview = false,
    contentType,
    streamData,
    hasError,
}) {
    if (_.isEqual(contentType, "JSON_FORM")) {
        return isDragPreview ? (
            <Tag minimal icon={faIcon({ icon: faPenLine })}>
                FORM
            </Tag>
        ) : (
            <JsonForm
                content={_.last(streamData).content}
                hasError={hasError}
            />
        );
    }
    return streamData.map((e, index) => {
        const { dataType, content, id } = e;
        if (_.includes(["STR", "INT", "FLOAT"], dataType)) {
            return <span key={id}>{(index ? " " : "") + content}</span>;
        } else if (_.isEqual(dataType, "JSON")) {
            return <JsonViewer key={id} json={content} />;
        }
        return null;
    });
}

import JsonForm from "@/components/sessions/message/renderers/JsonForm";
import JsonViewer from "@/components/sessions/message/renderers/JsonViewer";
import _ from "lodash";
export default function MessageContent({ contentType, streamData, hasError }) {
    return _.isEqual(contentType, "JSON_FORM") ? (
        <JsonForm content={_.last(streamData).content} hasError={hasError} />
    ) : (
        streamData.map((e, index) => {
            const { dataType, content, id } = e;
            if (_.includes(["STR", "INT", "FLOAT"], dataType)) {
                return <span key={id}>{(index ? " " : "") + content}</span>;
            } else if (_.isEqual(dataType, "JSON")) {
                return (
                    <JsonViewer displaySize={true} key={id} json={content} />
                );
            }
            return null;
        })
    );
}

import { FAIcon } from "@/components/FAIcon";
import JsonViewer from "@/components/JsonViewer";
import { Tag } from "@blueprintjs/core";
import {
    faBracketsCurly,
    faPenLine,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
const PreviewTag = ({ contentType, icon }) => {
    return (
        <Tag minimal icon={<FAIcon icon={icon} />}>
            {contentType}
        </Tag>
    );
};
export default function MessageContent({
    isPreview = false,
    contentType,
    streamData,
    hasError,
}) {
    const lastStreamData = _.last(streamData);
    if (_.isEqual(contentType, "JSON_FORM") && !_.isEmpty(lastStreamData)) {
        if (isPreview) {
            return <PreviewTag contentType={contentType} icon={faPenLine} />;
        }
        return null;
    }
    return streamData.map((data, index) => {
        const { dataType, content, id } = data;
        if (_.includes(["STR", "INT", "FLOAT"], dataType)) {
            return <span key={id}>{(index ? " " : "") + content}</span>;
        } else if (_.isEqual(dataType, "JSON")) {
            if (isPreview) {
                return (
                    <PreviewTag
                        contentType={contentType}
                        icon={faBracketsCurly}
                    />
                );
            }
            return <JsonViewer key={id} json={content} />;
        }
        return null;
    });
}

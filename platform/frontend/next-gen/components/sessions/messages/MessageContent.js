import { FAIcon } from "@/components/FAIcon";
import JSONViewer from "@/components/JSONViewer";
import { Classes, Tag } from "@blueprintjs/core";
import {
    faBracketsCurly,
    faPenLine,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import JSONForm from "./renderers/JSONForm";
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
    if (_.isEmpty(streamData)) {
        return <div className={Classes.SKELETON}>-</div>;
    }
    const lastStreamData = _.last(streamData);
    if (_.isEqual(contentType, "JSON_FORM")) {
        if (isPreview) {
            return <PreviewTag contentType={contentType} icon={faPenLine} />;
        }
        return (
            <JSONForm content={lastStreamData.content} hasError={hasError} />
        );
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
            return <JSONViewer key={id} json={content} />;
        }
        return null;
    });
}

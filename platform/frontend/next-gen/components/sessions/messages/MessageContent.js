import { FAIcon } from "@/components/FAIcon";
import JSONViewer from "@/components/JSONViewer";
import { Classes } from "@blueprintjs/core";
import {
    faBracketsCurly,
    faExclamation,
    faPenLine,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import _ from "lodash";
import Error from "./renderers/Error";
import JSONForm from "./renderers/JSONForm";
const PreviewTag = ({ contentType, icon }) => {
    return (
        <div>
            <FAIcon icon={icon} />
            &nbsp;{contentType}
        </div>
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
    } else if (_.isEqual(contentType, "ERROR")) {
        if (isPreview) {
            return (
                <PreviewTag contentType={contentType} icon={faExclamation} />
            );
        }
        return <Error content={lastStreamData.content} />;
    }
    return streamData.map((data, index) => {
        const { dataType, content, id } = data;
        if (_.includes(["STR", "INT", "FLOAT"], dataType)) {
            return <span key={id}>{(index ? " " : "") + content}</span>;
        } else if (_.isEqual(dataType, "JSON")) {
            if (isPreview) {
                return (
                    <PreviewTag
                        key={id}
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

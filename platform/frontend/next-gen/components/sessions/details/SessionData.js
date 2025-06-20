import JSONEditor from "@/components/codemirror/JSONEditor";
import {
    getUpdatePropertyPromises,
    settlePromises,
    shallowDiff,
} from "@/components/helper";
import { Size } from "@blueprintjs/core";
import axios from "axios";
import _ from "lodash";
import { useEffect, useRef, useState } from "react";
export default function SessionData({ sessionId }) {
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState({});
    const breaker = useRef(true);
    useEffect(() => {
        setLoading(true);
        axios
            .get(`/sessions/session/${sessionId}/data`)
            .then((response) => {
                setData(_.get(response, "data.result", {}));
                breaker.current = false;
            })
            .finally(() => {
                setLoading(false);
            });
    }, [sessionId]);
    const onSave = (value) => {
        setLoading(true);
        const diffs = shallowDiff(data, value);
        const promises = getUpdatePropertyPromises({
            axios,
            url: `/sessions/session/${sessionId}/data`,
            diffs,
            properties: value,
        });
        settlePromises(promises, ({ error }) => {
            if (!error) {
                setData(value);
            }
            setLoading(false);
        });
    };
    return (
        <div className="full-parent-dimension" style={{ padding: 20 }}>
            <JSONEditor
                className="custom-card"
                loading={loading}
                breaker={breaker}
                controlStripProps={{ size: Size.LARGE }}
                jsonObject={data}
                onSave={onSave}
            />
        </div>
    );
}

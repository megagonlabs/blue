import _ from "lodash";
import mermaid from "mermaid";
import { useCallback, useEffect, useState } from "react";
let instance_count;
export default function MermaidDiagram(props) {
    const [element, setElement] = useState();
    const [render_result, setRenderResult] = useState();
    if (_.isUndefined(instance_count)) {
        instance_count = 0;
    }
    const container_id = `${props.id || "d" + instance_count++}-mermaid`;
    const diagram_text = props.children;
    const render_js = !props.disableJs;
    // initialize mermaid here, but beware that it gets called once for every instance of the component
    useEffect(() => {
        // wait for page to load before initializing mermaid
        if (render_js)
            mermaid.initialize({
                startOnLoad: true,
                securityLevel: props.securityLevel || "strict",
                theme: props.theme || "default",
                logLevel: props.logLevel || 5,
            });
    }, [props.securityLevel, props.theme, props.logLevel]);
    // hook to track updates to the component ref, compatible with useEffect unlike useRef
    const updateDiagramRef = useCallback((elem) => {
        if (!elem) return;
        setElement(elem);
    }, []);
    // hook to update the component when either the element or the rendered diagram changes
    useEffect(() => {
        if (!element) return;
        if (!render_result?.svg) return;
        element.innerHTML = render_result.svg;
        render_result.bindFunctions?.(element);
    }, [element, render_result]);
    // hook to handle the diagram rendering
    useEffect(() => {
        if (!diagram_text && _.isEmpty(diagram_text)) return;
        // create async function inside useEffect to cope with async mermaid.run
        if (render_js)
            (async () => {
                try {
                    const rr = await mermaid.render(
                        `${container_id}-svg`,
                        diagram_text
                    );
                    setRenderResult(rr);
                } catch (error) {
                    props.onError?.(error);
                }
            })();
    }, [diagram_text, props]);
    // render container (div) to hold diagram (nested SVG)
    return (
        <div
            className={props.className}
            onClick={props.onClick}
            id={container_id}
            data-testid={props.testId}
            ref={updateDiagramRef}
        >
            {render_js}
        </div>
    );
}

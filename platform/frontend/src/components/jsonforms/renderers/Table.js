import { Callout, Code, HTMLTable, Intent } from "@blueprintjs/core";
import { rankWith, uiTypeIs } from "@jsonforms/core";
import {
    JsonFormsDispatch,
    withJsonFormsArrayControlProps,
} from "@jsonforms/react";
import _ from "lodash";
const TableRenderer = ({ cells, path, renderers, schema, uischema, data }) => {
    const style = _.get(uischema, "props.style", {});
    const compact = _.get(uischema, "props.compact", false);
    const striped = _.get(uischema, "props.striped", false);
    const bordered = _.get(uischema, "props.bordered", false);
    const columns = _.get(uischema, "columns", []);
    const rowCells = _.get(uischema, "rowCells", []);
    if (_.isNil(data) || !_.isArray(data))
        return (
            <Callout icon={null} intent={Intent.DANGER}>
                <Code>scope</Code> &#40;{uischema.scope}&#41; is invalid; data
                is either undefined or not an array.
            </Callout>
        );
    else if (_.size(columns) != _.size(rowCells))
        return (
            <Callout intent={Intent.DANGER} icon={null}>
                Number of columns doesn&apos;t match the number of rowCells.
                <br />
                {_.size(columns)} columns, {_.size(rowCells)} rowCells.
            </Callout>
        );
    return (
        <div className="full-parent-width" style={{ overflow: "auto" }}>
            <HTMLTable
                style={style}
                compact={compact}
                striped={striped}
                bordered={bordered}
            >
                <thead>
                    {columns.map((column, index) => (
                        <th key={index}>{column}</th>
                    ))}
                </thead>
                <tbody>
                    {data.map((element, dataIndex) => (
                        <tr key={dataIndex}>
                            {rowCells.map((cell, cellIndex) => (
                                <td key={cellIndex}>
                                    <JsonFormsDispatch
                                        schema={schema}
                                        uischema={cell}
                                        path={`${path}.${dataIndex}`}
                                        renderers={renderers}
                                        cells={cells}
                                    />
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </HTMLTable>
        </div>
    );
};
export default withJsonFormsArrayControlProps(TableRenderer);
export const TableTester = rankWith(3, uiTypeIs("Table"));

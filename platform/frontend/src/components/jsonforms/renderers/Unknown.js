import { Callout, Colors, Intent } from "@blueprintjs/core";
import { rankWith } from "@jsonforms/core";
import { withJsonFormsCellProps } from "@jsonforms/react";
const UnknownRenderer = ({ uischema }) => {
    return (
        <div
            style={{
                backgroundColor: Colors.WHITE,
                border: `2px dashed ${Colors.RED3}`,
                borderRadius: 2,
                wordWrap: "break-word",
            }}
        >
            <Callout icon={null} intent={Intent.DANGER}>
                No applicable renderer found for {JSON.stringify(uischema)}.
            </Callout>
        </div>
    );
};
export default withJsonFormsCellProps(UnknownRenderer);
export const UnknownTester = rankWith(0, () => true);

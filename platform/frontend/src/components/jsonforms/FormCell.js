import { FormGroup } from "@blueprintjs/core";
export default function FormCell({
    inline,
    style,
    label,
    labelInfo,
    helperText,
    children,
}) {
    return (
        <FormGroup
            contentClassName="full-parent-width"
            fill
            inline={inline}
            style={style}
            label={label}
            labelInfo={labelInfo}
            helperText={helperText}
        >
            {children}
        </FormGroup>
    );
}

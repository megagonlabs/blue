import { UICallout } from "./UICallout";
export function CardListCallout() {
    return (
        <UICallout
            id="card_list_double_right_click_callout"
            content={
                <div>
                    Double-click a card to open it in the current window.
                    Right-click &#40;when the context-menu cursor shows&#41; for
                    more options.
                </div>
            }
        />
    );
}

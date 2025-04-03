import {
    Button,
    ButtonVariant,
    ControlGroup,
    InputGroup,
    Intent,
    Size,
} from "@blueprintjs/core";
import {
    faBarsFilter,
    faSearch,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { FAIcon } from "../FAIcon";
import withAutoSizer from "../hocs/withAutoSizer";
function AgentList({ width, height }) {
    return (
        <div style={{ width, height }}>
            <div className="full-parent-dimension" style={{ padding: 20 }}>
                <ControlGroup>
                    <Button
                        size={Size.LARGE}
                        icon={<FAIcon icon={faBarsFilter} />}
                        variant={ButtonVariant.OUTLINED}
                        intent={Intent.PRIMARY}
                        text="Filter"
                    />
                    <InputGroup
                        leftIcon={<FAIcon icon={faSearch} />}
                        size={Size.LARGE}
                    />
                </ControlGroup>
            </div>
        </div>
    );
}
export default withAutoSizer(AgentList);

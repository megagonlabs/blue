import { AppContext } from "@/components/app-context";
import { faIcon } from "@/components/icon";
import {
    Button,
    ButtonGroup,
    Classes,
    Menu,
    MenuItem,
    Popover,
    Tooltip,
} from "@blueprintjs/core";
import { faArrowLeft, faArrowRight } from "@fortawesome/pro-duotone-svg-icons";
import _ from "lodash";
import { useContext } from "react";
export default function Pagination({
    type,
    page,
    setPage,
    pageSize,
    setPageSize,
}) {
    const { appState } = useContext(AppContext);
    return (
        <ButtonGroup style={{ width: 250 }} fill large>
            <Tooltip content="Previous" placement="bottom" minimal>
                <Button
                    className={appState[type].loading ? Classes.SKELETON : null}
                    onClick={() => setPage(page - 1)}
                    disabled={page < 1}
                    outlined
                    icon={faIcon({ icon: faArrowLeft })}
                />
            </Tooltip>
            <Button disabled minimal text={page + 1} />
            <Tooltip content="Next" placement="bottom" minimal>
                <Button
                    className={appState[type].loading ? Classes.SKELETON : null}
                    disabled={_.isEmpty(appState[type].list)}
                    onClick={() => setPage(page + 1)}
                    outlined
                    icon={faIcon({ icon: faArrowRight })}
                />
            </Tooltip>
            <Popover
                minimal
                placement="bottom-end"
                content={
                    <Menu>
                        {[10, 25, 50].map((size) => {
                            return (
                                <MenuItem
                                    text={size}
                                    key={`agent-registry-page-size-${size}`}
                                    disabled={_.isEqual(pageSize, size)}
                                    onClick={() => setPageSize(size)}
                                />
                            );
                        })}
                    </Menu>
                }
            >
                <Button
                    className={appState[type].loading ? Classes.SKELETON : null}
                    alignText="right"
                    style={{ width: 125 }}
                    outlined
                    text={`${pageSize} per page`}
                />
            </Popover>
        </ButtonGroup>
    );
}

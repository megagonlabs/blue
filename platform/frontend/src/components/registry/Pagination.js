import { AppContext } from "@/components/contexts/app-context";
import { faIcon } from "@/components/icon";
import {
    Button,
    ButtonGroup,
    Classes,
    Popover,
    Tooltip,
} from "@blueprintjs/core";
import {
    faArrowLeft,
    faArrowRight,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
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
        <ButtonGroup style={{ width: 224 }} fill size="large">
            <Tooltip content="Previous" placement="bottom" minimal>
                <Button
                    className={appState[type].loading ? Classes.SKELETON : null}
                    onClick={() => setPage(page - 1)}
                    disabled={page < 1}
                    variant="outlined"
                    icon={faIcon({ icon: faArrowLeft })}
                />
            </Tooltip>
            <Button variant="minimal" disabled text={page + 1} />
            <Tooltip content="Next" placement="bottom" minimal>
                <Button
                    className={appState[type].loading ? Classes.SKELETON : null}
                    disabled={_.isEmpty(appState[type].list)}
                    onClick={() => setPage(page + 1)}
                    variant="outlined"
                    icon={faIcon({ icon: faArrowRight })}
                />
            </Tooltip>
            <Popover
                minimal
                placement="bottom-end"
                content={
                    <div style={{ padding: 15, width: 150 }}>
                        {[10, 25, 50].map((size) => {
                            return (
                                <Button
                                    fill
                                    variant="minimal"
                                    text={size}
                                    key={size}
                                    disabled={_.isEqual(pageSize, size)}
                                    onClick={() => setPageSize(size)}
                                />
                            );
                        })}
                    </div>
                }
            >
                <Button
                    className={appState[type].loading ? Classes.SKELETON : null}
                    alignText="right"
                    style={{ width: 100 }}
                    variant="outlined"
                    text={`${pageSize} / page`}
                />
            </Popover>
        </ButtonGroup>
    );
}

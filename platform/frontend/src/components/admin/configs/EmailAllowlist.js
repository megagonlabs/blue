import { faIcon } from "@/components/icon";
import {
    Button,
    Classes,
    Code,
    ControlGroup,
    InputGroup,
    Intent,
    Section,
    SectionCard,
    Tag,
    Tooltip,
} from "@blueprintjs/core";
import {
    Cell,
    Column,
    ColumnHeaderCell,
    RowHeaderCell,
    Table2,
} from "@blueprintjs/table";
import {
    faTrash,
    faUserPlus,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import axios from "axios";
import classNames from "classnames";
import _ from "lodash";
import { useEffect, useMemo, useState } from "react";
export default function EmailAllowlist({ loading, configs }) {
    const allowedDomains = _.get(configs, "allowed_domains", []);
    const [allowedEmails, setAllowedEmails] = useState([]);
    const [saving, setSaving] = useState(false);
    const [userByEmail, setUserByEmail] = useState({});
    useEffect(() => {
        const emailList = Object.entries(_.get(configs, "allowed_emails", {}))
            .filter((email) => _.get(email, [1, "allow"], false))
            .map((email) => ({ email: _.get(email, [1, "email"]) }));
        setAllowedEmails(emailList);
        let tasks = [];
        for (let i = 0; i < _.size(emailList); i++) {
            tasks.push(
                new Promise((resolve, reject) => {
                    axios
                        .get(`/accounts/profile/email/${emailList[i].email}`)
                        .then((response) => {
                            resolve(response);
                        })
                        .catch((error) => reject(error));
                })
            );
        }
        Promise.allSettled(tasks).then((results) => {
            let mappings = {};
            for (let i = 0; i < _.size(results); i++) {
                if (
                    (_.isEqual(_.get(results, [i, "status"], null)),
                    "fulfilled")
                ) {
                    const user = _.get(
                        results,
                        [i, "value", "data", "user"],
                        {}
                    );
                    if (_.has(user, "email")) {
                        mappings[user.email] = user;
                    }
                }
            }
            setUserByEmail(mappings);
        });
    }, [configs]);
    const [emailAddress, setEmailAddress] = useState("");
    const removeAlowedEmail = (email) => {
        setSaving(true);
        axios
            .delete(`/platform/settings/allowed_emails/${email}`)
            .then(() => {
                setAllowedEmails(
                    allowedEmails.filter(
                        (element) => !_.isEqual(_.get(element, "email"), email)
                    )
                );
            })
            .finally(() => {
                setSaving(false);
            });
    };
    const addAllowedEmail = () => {
        setSaving(true);
        axios
            .put(`/platform/settings/allowed_emails/${emailAddress}`)
            .then(() => {
                setAllowedEmails(
                    _.uniqBy(
                        [...allowedEmails, { email: emailAddress }],
                        "email"
                    )
                );
                axios
                    .get(`/accounts/profile/email/${emailAddress}`)
                    .then((response) => {
                        const user = _.get(response, "data.user", {});
                        if (_.has(user, "email"))
                            setUserByEmail({
                                ...userByEmail,
                                [user.email]: user,
                            });
                    });
                setEmailAddress("");
            })
            .finally(() => {
                setSaving(false);
            });
    };
    const [tableKey, setTableKey] = useState(Date.now());
    const TABLE_CELL_HEIGHT = 40;
    const columns = useMemo(() => {
        return [
            {
                name: "UID",
                key: "uid",
                cellRenderer: (rowIndex) => {
                    return (
                        <Cell
                            style={{ lineHeight: `${TABLE_CELL_HEIGHT - 1}px` }}
                        >
                            {_.get(
                                userByEmail,
                                [
                                    _.get(allowedEmails, [rowIndex, "email"]),
                                    "uid",
                                ],
                                "-"
                            )}
                        </Cell>
                    );
                },
            },
            {
                name: "Name",
                key: "name",
                cellRenderer: (rowIndex) => {
                    return (
                        <Cell
                            style={{ lineHeight: `${TABLE_CELL_HEIGHT - 1}px` }}
                        >
                            {_.get(
                                userByEmail,
                                [
                                    _.get(allowedEmails, [rowIndex, "email"]),
                                    "name",
                                ],
                                "-"
                            )}
                        </Cell>
                    );
                },
            },
            { name: "Email", key: "email" },
            {
                name: "Action",
                key: "action",
                cellRenderer: (rowIndex) => (
                    <Cell style={{ lineHeight: `${TABLE_CELL_HEIGHT - 1}px` }}>
                        <Tooltip content="Remove" minimal placement="left">
                            <Button
                                loading={saving}
                                onClick={() =>
                                    removeAlowedEmail(
                                        _.get(allowedEmails, [
                                            rowIndex,
                                            "email",
                                        ])
                                    )
                                }
                                intent={Intent.DANGER}
                                variant="minimal"
                                icon={faIcon({ icon: faTrash })}
                            />
                        </Tooltip>
                    </Cell>
                ),
            },
        ];
    }, [userByEmail, allowedEmails, saving]);
    useEffect(() => {
        setTableKey(Date.now());
    }, [columns]);
    return (
        <Section compact title="Email Allowlist">
            <SectionCard>
                <div>Allowed domains</div>
                <div
                    style={{ marginTop: 5, marginBottom: 10 }}
                    className={classNames(
                        Classes.TEXT_SMALL,
                        Classes.TEXT_MUTED
                    )}
                >
                    Can only be configured through server environment
                    variable:&nbsp;<Code>BLUE_EMAIL_DOMAIN_WHITE_LIST</Code>.
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
                    {allowedDomains.map((domain) => (
                        <Tag size="large" minimal>
                            {domain}
                        </Tag>
                    ))}
                </div>
            </SectionCard>
            <SectionCard>
                <div>Allowed emails</div>
                <div
                    style={{ marginTop: 5, marginBottom: 10 }}
                    className={classNames(
                        Classes.TEXT_SMALL,
                        Classes.TEXT_MUTED
                    )}
                >
                    In addition to allowed domains, Google accounts with emails
                    whitelisted here can also sign in on the platform.
                </div>
                <div>
                    <ControlGroup>
                        <InputGroup
                            onValueChange={(value) => {
                                setEmailAddress(value);
                            }}
                            size="large"
                            style={{ width: 200 }}
                            value={emailAddress}
                        />
                        <Button
                            intent={Intent.PRIMARY}
                            size="large"
                            variant="minimal"
                            icon={faIcon({ icon: faUserPlus })}
                            text="Add"
                            loading={saving}
                            disabled={_.isEmpty(_.trim(emailAddress))}
                            onClick={addAllowedEmail}
                        />
                    </ControlGroup>
                    <div style={{ height: 300, marginTop: 10 }}>
                        <Table2
                            minColumnWidth={62}
                            key={tableKey}
                            enableRowResizing={false}
                            numRows={allowedEmails.length}
                            enableColumnReordering={false}
                            defaultRowHeight={TABLE_CELL_HEIGHT}
                            rowHeaderCellRenderer={(rowIndex) => (
                                <RowHeaderCell
                                    name={
                                        <div
                                            style={{
                                                textAlign: "center",
                                                lineHeight: `${TABLE_CELL_HEIGHT}px`,
                                            }}
                                        >
                                            {rowIndex + 1}
                                        </div>
                                    }
                                />
                            )}
                        >
                            {columns.map((col, index) => {
                                const { name, key, cellRenderer } = col;
                                const defaultCellRenderer = (rowIndex) => (
                                    <Cell
                                        style={{
                                            lineHeight: `${
                                                TABLE_CELL_HEIGHT - 1
                                            }px`,
                                        }}
                                    >
                                        {_.get(
                                            allowedEmails,
                                            [rowIndex, key],
                                            "-"
                                        )}
                                    </Cell>
                                );
                                const menuRenderer = null;
                                const columnHeaderCellRenderer = () => (
                                    <ColumnHeaderCell
                                        name={
                                            <span style={{ fontWeight: 600 }}>
                                                {name}
                                            </span>
                                        }
                                        menuRenderer={menuRenderer}
                                    />
                                );
                                return (
                                    <Column
                                        cellRenderer={(rowIndex) =>
                                            _.isFunction(cellRenderer)
                                                ? cellRenderer.call(
                                                      null,
                                                      rowIndex
                                                  )
                                                : defaultCellRenderer.call(
                                                      null,
                                                      rowIndex
                                                  )
                                        }
                                        columnHeaderCellRenderer={
                                            columnHeaderCellRenderer
                                        }
                                        key={`${key}-${index}`}
                                        name={name}
                                    />
                                );
                            })}
                        </Table2>
                    </div>
                </div>
            </SectionCard>
        </Section>
    );
}

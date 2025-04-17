import { useDedupStore } from "@/stores/dedup-store";
import { Card, Classes, Colors } from "@blueprintjs/core";
import classNames from "classnames";
import _ from "lodash";
import Image from "next/image";
export default function UserAvatar({ userId }) {
    const users = useDedupStore((state) => state.users);
    return (
        <Card
            className={classNames("padding-0", "overflow-hidden", {
                [Classes.SKELETON]: !_.has(users, userId),
            })}
            style={{
                height: 40,
                width: 40,
                borderRadius: "50%",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                backgroundColor: Colors.WHITE,
            }}
        >
            <Image
                alt=""
                src={_.get(users, [userId, "picture"], "")}
                width={40}
                height={40}
            />
        </Card>
    );
}

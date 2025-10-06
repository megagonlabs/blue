import { useDedupStore } from "@/stores/dedup-store";
import { Classes, Colors } from "@blueprintjs/core";
import classNames from "classnames";
import _ from "lodash";
import Image from "next/image";
export default function UserAvatar({ userId, size = 40 }) {
    const users = useDedupStore((state) => state.users);
    return (
        <div
            className={classNames(
                "padding-0",
                "overflow-hidden",
                "custom-card",
                { [Classes.SKELETON]: !_.has(users, userId) }
            )}
            style={{
                height: size,
                width: size,
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
                width={size}
                height={size}
            />
        </div>
    );
}

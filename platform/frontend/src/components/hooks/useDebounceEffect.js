import { useEffect } from "react";
export function useDebounceEffect(fn, waitTime, deps) {
    useEffect(() => {
        const t = setTimeout(() => {
            fn.apply(undefined, deps);
        }, waitTime);

        return () => {
            clearTimeout(t);
        };
    }, deps);
}

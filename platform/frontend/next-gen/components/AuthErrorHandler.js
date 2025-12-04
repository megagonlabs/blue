import { useAuthStore } from "@/stores/auth-store";
import axios from "axios";
import _ from "lodash";
import { useCallback, useEffect, useRef } from "react";
import { useShallow } from "zustand/react/shallow";
export default function AuthErrorHandler({ children }) {
    const { user, clearUser } = useAuthStore(
        useShallow((state) => ({
            user: state.user,
            clearUser: state.clearUser,
        }))
    );
    useEffect(() => {
        const responseInterceptor = axios.interceptors.response.use(
            (response) => response,
            async (error) => {
                if (error.response && _.isEqual(error.response.status, 401)) {
                    clearUser();
                }
                return Promise.reject(error);
            }
        );
        return () => {
            axios.interceptors.response.eject(responseInterceptor);
        };
    }, [clearUser]);
    const timeoutIdRef = useRef(null); // ref to store the timeoutId
    const checkAuthSession = useCallback(async () => {
        if (!user) return;
        try {
            await axios.get("/accounts/profile");
            timeoutIdRef.current = setTimeout(
                checkAuthSession,
                2 * 60 * 1000 // 2 minutes
            );
        } catch (error) {}
    }, [user]);
    useEffect(() => {
        checkAuthSession();
        return () => {
            if (timeoutIdRef.current) {
                clearTimeout(timeoutIdRef.current);
            }
        };
    }, [checkAuthSession]);
    return children;
}

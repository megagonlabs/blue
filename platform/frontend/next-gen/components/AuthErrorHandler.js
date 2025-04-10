import { useAuthStore } from "@/stores/auth-store";
import axios from "axios";
import _ from "lodash";
import { useEffect } from "react";
export default function AuthErrorHandler({ children }) {
    const clearUser = useAuthStore((state) => state.clearUser);
    useEffect(() => {
        const responseInterceptor = axios.interceptors.response.use(
            (response) => response,
            async (error) => {
                if (error.response && _.isEqual(error.response.status, 401))
                    clearUser();
                return Promise.reject(error);
            }
        );
        return () => {
            axios.interceptors.response.eject(responseInterceptor);
        };
    }, [clearUser]);
    return children;
}

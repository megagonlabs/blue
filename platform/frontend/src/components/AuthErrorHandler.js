import axios from "axios";
import _ from "lodash";
import { useContext, useEffect } from "react";
import { AuthContext } from "./contexts/auth-context";
const AuthErrorHandler = ({ children }) => {
    const { clearAuth } = useContext(AuthContext);
    useEffect(() => {
        const responseInterceptor = axios.interceptors.response.use(
            (response) => response,
            async (error) => {
                if (error.response && _.isEqual(error.response.status, 401)) {
                    clearAuth();
                }
                return Promise.reject(error);
            }
        );
        return () => {
            axios.interceptors.response.eject(responseInterceptor);
        };
    }, [clearAuth]);
    return children;
};
export default AuthErrorHandler;

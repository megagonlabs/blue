import { useToaster } from "@/components/contexts/ToasterContext";
import {
    Button,
    ButtonVariant,
    Callout,
    Classes,
    Colors,
    Dialog,
    DialogBody,
    Intent,
    Size,
} from "@blueprintjs/core";
import axios from "axios";
import { initializeApp } from "firebase/app";
import { GoogleAuthProvider, getAuth, signInWithPopup } from "firebase/auth";
import _ from "lodash";
import Head from "next/head";
import { useEffect, useState } from "react";
// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyBgwI0-HcszkCrtMf5EnVH4i8J6AAiQk3Q",
    authDomain: "blue-public.firebaseapp.com",
    projectId: "blue-public",
    storageBucket: "blue-public.firebasestorage.app",
    messagingSenderId: "342414327441",
    appId: "1:342414327441:web:477d438a75d0d406e3c930",
    measurementId: "G-M74783LTXN",
};
// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();
const GOOGLE_LOGO_SVG = (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="18"
        height="18"
        viewBox="0 0 18 18"
        fill="none"
        role="img"
    >
        <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M17.64 9.20419C17.64 8.56601 17.5827 7.95237 17.4764 7.36328H9V10.8446H13.8436C13.635 11.9696 13.0009 12.9228 12.0477 13.561V15.8192H14.9564C16.6582 14.2524 17.64 11.9451 17.64 9.20419Z"
            fill="#4285F4"
        ></path>
        <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M8.99976 18C11.4298 18 13.467 17.1941 14.9561 15.8195L12.0475 13.5613C11.2416 14.1013 10.2107 14.4204 8.99976 14.4204C6.65567 14.4204 4.67158 12.8372 3.96385 10.71H0.957031V13.0418C2.43794 15.9831 5.48158 18 8.99976 18Z"
            fill="#34A853"
        ></path>
        <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M3.96409 10.7098C3.78409 10.1698 3.68182 9.59301 3.68182 8.99983C3.68182 8.40664 3.78409 7.82983 3.96409 7.28983V4.95801H0.957273C0.347727 6.17301 0 7.54755 0 8.99983C0 10.4521 0.347727 11.8266 0.957273 13.0416L3.96409 10.7098Z"
            fill="#FBBC05"
        ></path>
        <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M8.99976 3.57955C10.3211 3.57955 11.5075 4.03364 12.4402 4.92545L15.0216 2.34409C13.4629 0.891818 11.4257 0 8.99976 0C5.48158 0 2.43794 2.01682 0.957031 4.95818L3.96385 7.29C4.67158 5.16273 6.65567 3.57955 8.99976 3.57955Z"
            fill="#EA4335"
        ></path>
    </svg>
);
export default function Index() {
    const [loading, setLoading] = useState(true);
    const [done, setDone] = useState(false);
    const [profile, setProfile] = useState(null);
    const [ws, setWs] = useState(null);
    const { appToaster } = useToaster();
    useEffect(() => {
        setLoading(true);
        const server = "localhost:25831";
        const socket = new WebSocket(`ws://${server}`);
        socket.onopen = () => {
            socket.send(JSON.stringify("REQUEST_CONNECTION_INFO"));
            setLoading(false);
            if (appToaster) {
                appToaster.show({
                    intent: Intent.SUCCESS,
                    message: `Connected to Blue CLI`,
                });
            }
        };
        socket.onmessage = (event) => {
            try {
                // parse the data from string to JSON object
                const data = JSON.parse(event.data);
                const type = _.get(data, "type", null);
                const message = _.get(data, "message", null);
                if (_.isEqual(type, "REQUEST_CONNECTION_INFO")) {
                    setProfile(message);
                } else if (_.has(data, "error")) {
                    if (appToaster) {
                        appToaster.show({
                            intent: Intent.DANGER,
                            message: data.error,
                        });
                    }
                } else if (_.isEqual(data, "DONE")) {
                    setDone(true);
                    socket.close();
                }
            } catch (e) {
                if (appToaster) {
                    appToaster.show({
                        intent: Intent.WARNING,
                        message: e,
                    });
                }
                console.log(event.data);
                console.error(e);
            }
        };
        socket.onerror = () => {
            setWs(null);
            setLoading(false);
            if (appToaster) {
                appToaster.show({
                    intent: Intent.DANGER,
                    message: `WebSocket connection to 'ws://${server}' failed`,
                });
            }
        };
        setWs(socket);
    }, []);
    const [popupOpen, setPopupOpen] = useState(false);
    const signInWithGoogle = () => {
        const server = _.get(profile, "BLUE_PUBLIC_API_SERVER", null);
        const secure =
            _.toLower(_.get(profile, "BLUE_DEPLOY_SECURE", "True")) == "true";
        const port = _.get(profile, "BLUE_PUBLIC_API_SERVER_PORT", null);
        const platformName = _.get(profile, "BLUE_DEPLOY_PLATFORM", null);
        setPopupOpen(true);
        signInWithPopup(auth, provider)
            .then((result) => {
                result.user.getIdToken().then((idToken) => {
                    axios
                        .post(
                            `http${
                                secure ? "s" : ""
                            }://${server}:${port}/blue/platform/${platformName}/accounts/sign-in/cli`,
                            { id_token: idToken }
                        )
                        .then((response) => {
                            const cookie = _.get(response, "data.cookie", null),
                                uid = _.get(response, "data.uid", null);
                            ws.send(JSON.stringify({ cookie, uid }));
                            setPopupOpen(false);
                        })
                        .catch(() => {
                            setPopupOpen(false);
                        });
                });
            })
            .catch((error) => {
                setPopupOpen(false);
                if (appToaster) {
                    appToaster.show({
                        intent: Intent.DANGER,
                        message: `${error.code ? `[${error.code}]` : ""} ${
                            error.message
                        }`,
                    });
                }
            });
    };
    return (
        <>
            <Head>
                <title>Blue CLI</title>
                <meta
                    name="viewport"
                    content="width=device-width, initial-scale=1"
                />
                <link rel="icon" href="/images/favicon.ico" />
            </Head>
            {done ? (
                <div style={{ padding: 15 }}>
                    <Callout intent={Intent.SUCCESS}>
                        Authentication details received, processing details. You
                        may close this window at any time.
                    </Callout>
                </div>
            ) : (
                <Dialog
                    autoFocus
                    enforceFocus
                    style={{ maxWidth: 300, backgroundColor: Colors.WHITE }}
                    isCloseButtonShown={false}
                    title="Blue CLI"
                    isOpen
                >
                    {_.isNil(ws) ? (
                        <Callout
                            style={{ borderRadius: 0 }}
                            intent={Intent.DANGER}
                            icon={null}
                        >
                            Unable to connect to Blue CLI
                        </Callout>
                    ) : null}
                    <DialogBody>
                        <Button
                            loading={popupOpen}
                            disabled={_.isNil(ws)}
                            size={Size.LARGE}
                            variant={ButtonVariant.OUTLINED}
                            className={loading ? Classes.SKELETON : null}
                            text="Sign in with Google"
                            onClick={signInWithGoogle}
                            fill
                            icon={GOOGLE_LOGO_SVG}
                        />
                    </DialogBody>
                </Dialog>
            )}
        </>
    );
}

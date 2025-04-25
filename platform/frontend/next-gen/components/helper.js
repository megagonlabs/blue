const {
    faExclamation,
    faCopy,
} = require("@fortawesome/sharp-duotone-solid-svg-icons");
const { AppToaster } = require("./toaster");
const { FAIcon } = require("./FAIcon");
const { Intent } = require("@blueprintjs/core");
const copy = require("copy-to-clipboard");

module.exports = {
    waitForOpenConnection: (socket) => {
        return new Promise((resolve, reject) => {
            const maxNumberOfAttempts = 10;
            const intervalTime = 200; //ms
            let currentAttempt = 0;
            const interval = setInterval(() => {
                if (currentAttempt > maxNumberOfAttempts - 1) {
                    clearInterval(interval);
                    reject(new Error("Maximum number of attempts exceeded"));
                } else if (_.isEqual(socket.readyState, WebSocket.OPEN)) {
                    clearInterval(interval);
                    resolve();
                }
                currentAttempt++;
            }, intervalTime);
        });
    },
    showAxiosErrorToast: (error) => {
        let message = "";
        try {
            message = `${error.name}: ${error.message}`;
            // the request was made and the server responded with a status code
            // that falls out of the range of 2xx
            if (error.response)
                message = `[${error.response.status} ${
                    error.response.statusText
                }]: ${_.get(error, "response.data.message", "-")}`;
        } catch (error) {
            message = "Request Error";
        }
        AppToaster.show({
            icon: <FAIcon icon={faExclamation} />,
            intent: Intent.DANGER,
            message: <div className="multiline-ellipsis-5">{message}</div>,
            action: {
                icon: <FAIcon icon={faCopy} />,
                onClick: () => copy(message),
                text: "Copy",
            },
        });
    },
};

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
};

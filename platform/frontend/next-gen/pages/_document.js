import Document, { Head, Html, Main, NextScript } from "next/document";

class BlueDocument extends Document {
    render() {
        return (
            <Html lang="en">
                <Head></Head>
                <body style={{ overflow: "hidden" }}>
                    <Main />
                    <NextScript />
                </body>
            </Html>
        );
    }
}
export default BlueDocument;

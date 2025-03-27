import Document, { Head, Html, Main, NextScript } from "next/document";
class BlueDocument extends Document {
    render() {
        return (
            <Html lang="en">
                {/* eslint-disable-next-line @next/next/no-sync-scripts */}
                <script src="/__ENV.js" />
                <Head></Head>
                <body>
                    <Main />
                    <NextScript />
                </body>
            </Html>
        );
    }
}
export default BlueDocument;

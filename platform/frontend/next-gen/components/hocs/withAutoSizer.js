import AutoSizer from "react-virtualized-auto-sizer";
const withAutoSizer = (WrappedComponent) => {
    return (props) => (
        <AutoSizer>
            {({ height, width }) => (
                <WrappedComponent {...props} height={height} width={width} />
            )}
        </AutoSizer>
    );
};
export default withAutoSizer;

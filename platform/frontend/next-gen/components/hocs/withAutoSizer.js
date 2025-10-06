import AutoSizer from "react-virtualized-auto-sizer";
const withAutoSizer = (WrappedComponent) => {
    const HOC = (props) => (
        <AutoSizer>
            {({ height, width }) => (
                <WrappedComponent {...props} height={height} width={width} />
            )}
        </AutoSizer>
    );
    HOC.displayName = `withAutoSizer(${
        WrappedComponent.displayName || WrappedComponent.name || "Component"
    })`;
    return HOC;
};
export default withAutoSizer;

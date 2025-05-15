import withAutoSizer from "../hocs/withAutoSizer";
function SystemStatusContainer({ width, height }) {
    return <div style={{ width, height }}>system status</div>;
}
export default withAutoSizer(SystemStatusContainer);

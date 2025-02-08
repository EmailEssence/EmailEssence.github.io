import "./dashboard.css";

export default function Dashboard() {
  return (
    <div className="dashboard">
      <WeightedEmailList />
      <MiniViewPanel />
    </div>
  );
}

function WeightedEmailList() {
  return <div></div>;
}

function MiniViewPanel() {
  return (
    <div className="mini-view">
      <MiniViewHead />
      <MiniViewBody />
    </div>
  );
}

function MiniViewHead() {
  return <div></div>;
}

function MiniViewBody() {
  return <div></div>;
}

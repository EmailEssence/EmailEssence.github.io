/* eslint-disable react/prop-types */
import "./dashboard.css";

export default function Dashboard({ emailList, onPageComponent }) {
  return (
    <div className="dashboard">
      <WeightedEmailList emailList={emailList} />
      <MiniViewPanel emailList={emailList} onPageComponent={onPageComponent} />
    </div>
  );
}

function WeightedEmailList({ emailList }) {
  return <div></div>;
}

function MiniViewPanel({ emailList, onPageComponent }) {
  return (
    <div className="mini-view">
      <MiniViewHead onPageComponent={onPageComponent} />
      <MiniViewBody emailList={emailList} />
    </div>
  );
}

function MiniViewHead({ onPageComponent }) {
  return <div className="head-container"></div>;
}

function MiniViewBody({ emailList }) {
  return <div></div>;
}

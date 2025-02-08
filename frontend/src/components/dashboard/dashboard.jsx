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
  const emails = () => {
    const returnBlock = [];
    for (const email of emailList) {
      returnBlock.push(
        <WEListEmail key={emailList.indexOf(email)} email={email} />
      );
    }
    return returnBlock;
  };
  return <div className="weighted-email-list-container">{emails()}</div>;
}

function WEListEmail({ email }) {
  return (
    <div className="welist-email-container">
      <div className="summary">{email.summary}</div>
      <div className="email-link"></div>
    </div>
  );
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
  return (
    <div className="head-container">
      <div className="inbox-text-container">
        <div className="inbox-text"></div>
      </div>
      <div
        className="expand-button"
        onClick={() => onPageComponent("inbox")}
      ></div>
    </div>
  );
}

function MiniViewBody({ emailList }) {
  const emails = () => {
    const returnBlock = [];
    for (const email of emailList) {
      returnBlock.push(
        <MiniViewEmail key={emailList.indexOf(email)} email={email} />
      );
    }
    return returnBlock;
  };
  return <div className="body-container">{emails()}</div>;
}

function MiniViewEmail({ email }) {
  return (
    <div className="miniview-email-container">
      <div className="from">{email.from}</div>
      <div className="median"></div>
      <div className="summary">{email.summary}</div>
    </div>
  );
}

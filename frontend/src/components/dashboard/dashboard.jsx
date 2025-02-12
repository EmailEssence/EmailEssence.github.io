/* eslint-disable react/prop-types */
import FullScreenIcon from "../../assets/fullScreenIcon";
import "./dashboard.css";

export default function Dashboard({ emailList, getPageComponent }) {
  return (
    <div className="dashboard">
      <WeightedEmailList emailList={emailList} />
      <MiniViewPanel
        emailList={emailList}
        getPageComponent={getPageComponent}
      />
    </div>
  );
}

function WeightedEmailList({ emailList }) {
  const emails = () => {
    const returnBlock = [];
    for (let i = 0; i < 5; i++) {
      returnBlock.push(
        <WEListEmail key={emailList[i].email_id} email={emailList[i]} />
      );
    }
    return returnBlock;
  };
  return <div className="weighted-email-list-container">{emails()}</div>;
}

function WEListEmail({ email }) {
  return (
    <div className="welist-email-container">
      <div className="summary">{email.summary_text}</div>
      <div className="email-link"></div>
    </div>
  );
}

function MiniViewPanel({ emailList, getPageComponent }) {
  return (
    <div className="mini-view">
      <MiniViewHead getPageComponent={getPageComponent} />
      <MiniViewBody emailList={emailList} />
    </div>
  );
}

function MiniViewHead({ getPageComponent }) {
  return (
    <div className="head-container">
      <div className="inbox-text-container">
        <div className="inbox-icon">IN</div>
        <div className="inbox-text">Inbox</div>
      </div>
      <div className="expand-button" onClick={() => getPageComponent("inbox")}>
        <FullScreenIcon />
      </div>
    </div>
  );
}

function MiniViewBody({ emailList }) {
  const emails = () => {
    const returnBlock = [];
    for (const email of emailList) {
      returnBlock.push(<MiniViewEmail key={email.email_id} email={email} />);
    }
    return returnBlock;
  };
  return <div className="body-container">{emails()}</div>;
}

function MiniViewEmail({ email }) {
  return (
    <div className="miniview-email-container">
      <div className="from">{email.sender}</div>
      <div className="median"></div>
      <div className="subject">{email.subject}</div>
    </div>
  );
}

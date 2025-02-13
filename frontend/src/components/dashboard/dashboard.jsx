/* eslint-disable react/prop-types */
import FullScreenIcon from "../../assets/FullScreenIcon";
import "./miniview.css";
import "./weightedEmailList.css";

const getSenderName = (sender) => {
  return sender.slice(0, sender.indexOf("<"));
};

export default function Dashboard({ emailList, handlePageChange }) {
  return (
    <div className="dashboard">
      <WeightedEmailList emailList={emailList} />
      <MiniViewPanel
        emailList={emailList}
        handlePageChange={handlePageChange}
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

function MiniViewPanel({ emailList, handlePageChange }) {
  return (
    <div className="mini-view">
      <MiniViewHead handlePageChange={handlePageChange} />
      <MiniViewBody emailList={emailList} />
    </div>
  );
}

function MiniViewHead({ handlePageChange }) {
  return (
    <div className="head-container">
      <div className="inbox-text-container">
        <div className="inbox-icon">IN</div>
        <div className="inbox-text">Inbox</div>
      </div>
      <div className="expand-button" onClick={() => handlePageChange("inbox")}>
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
      <div className="from">{getSenderName(email.sender)}</div>
      <div className="median">
        <div className="medianfill"></div>
      </div>
      <div className="subject">{email.subject}</div>
    </div>
  );
}

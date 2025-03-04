/* eslint-disable react/prop-types */
import FullScreenIcon from "../../assets/FullScreenIcon";
import InboxIcon from "../../assets/InboxArrow";
// import ViewIcon from "../../assets/ViewIcon";
import "./miniview.css";
import "./weightedEmailList.css";

const getSenderName = (sender) => {
  return sender.slice(0, sender.indexOf("<"));
};

export default function Dashboard({
  emailList,
  handlePageChange,
  setCurEmail,
}) {
  return (
    <div className="dashboard">
      <WeightedEmailList
        emailList={emailList}
        setCurEmail={setCurEmail}
        handlePageChange={handlePageChange}
      />
      <MiniViewPanel
        emailList={emailList}
        handlePageChange={handlePageChange}
        setCurEmail={setCurEmail}
      />
    </div>
  );
}

function WeightedEmailList({ emailList, setCurEmail, handlePageChange }) {
  const emails = () => {
    const returnBlock = [];
    for (let i = 0; i < 5; i++) {
      returnBlock.push(
        <WEListEmail
          key={emailList[i].email_id}
          email={emailList[i]}
          setCurEmail={setCurEmail}
          handlePageChange={handlePageChange}
        />
      );
    }
    return returnBlock;
  };
  return <div className="weighted-email-list-container">{emails()}</div>;
}

function WEListEmail({ email, setCurEmail, handlePageChange }) {
  return (
    <div className="welist-email-container">
      <div className="summary">{email.summary_text}</div>
      <div
        className="email-link"
        onClick={() => {
          setCurEmail(email);
          handlePageChange("inbox");
        }}
      >
        {/* <ViewIcon /> */}
        <img src="./src/assets/oldAssets/ViewIcon.svg" alt="View Icon" />
      </div>
    </div>
  );
}

function MiniViewPanel({ emailList, handlePageChange, setCurEmail }) {
  return (
    <div className="mini-view">
      <MiniViewHead handlePageChange={handlePageChange} />
      <MiniViewBody
        emailList={emailList}
        setCurEmail={setCurEmail}
        handlePageChange={handlePageChange}
      />
    </div>
  );
}

function MiniViewHead({ handlePageChange }) {
  return (
    <div className="head-container">
      <div className="inbox-text-container">
        <div className="inbox-icon">
          <InboxIcon />
        </div>
        <div className="inbox-text">Inbox</div>
      </div>
      <div
        className="expand-button"
        role="button"
        onClick={() => handlePageChange("inbox")}
      >
        <FullScreenIcon />
      </div>
    </div>
  );
}

function MiniViewBody({ emailList, setCurEmail, handlePageChange }) {
  const emails = () => {
    const returnBlock = [];
    for (const email of emailList) {
      returnBlock.push(
        <MiniViewEmail
          key={email.email_id}
          email={email}
          setCurEmail={setCurEmail}
          handlePageChange={handlePageChange}
        />
      );
    }
    return returnBlock;
  };
  return <div className="body-container">{emails()}</div>;
}

function MiniViewEmail({ email, setCurEmail, handlePageChange }) {
  return (
    <div
      className="miniview-email-container"
      onClick={() => {
        setCurEmail(email);
        handlePageChange("inbox");
      }}
    >
      <div className="from">{getSenderName(email.sender)}</div>
      <div className="median">
        <div className="medianfill"></div>
      </div>
      <div className="subject">{email.subject}</div>
    </div>
  );
}

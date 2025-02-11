/* eslint-disable react/prop-types */
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
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="30"
          height="30"
          viewBox="0 0 30 30"
          fill="none"
        >
          <rect x="1" y="1" width="28" height="28" fill="white" />
          <path
            d="M27.9989 29.4999C28.8274 29.4999 29.4989 28.8283 29.4989 27.9999L29.4989 14.4999C29.4989 13.6715 28.8274 12.9999 27.9989 12.9999C27.1705 12.9999 26.4989 13.6715 26.4989 14.4999V26.4999H14.4989C13.6705 26.4999 12.9989 27.1715 12.9989 27.9999C12.9989 28.8283 13.6705 29.4999 14.4989 29.4999L27.9989 29.4999ZM15.327 17.4493L26.9383 29.0605L29.0596 26.9392L17.4484 15.328L15.327 17.4493Z"
            fill="#999999"
          />
          <path
            d="M1.9996 0.50012C1.17117 0.50012 0.499597 1.17169 0.499597 2.00012L0.499596 15.5001C0.499596 16.3285 1.17117 17.0001 1.9996 17.0001C2.82803 17.0001 3.4996 16.3285 3.4996 15.5001V3.50012H15.4996C16.328 3.50012 16.9996 2.82854 16.9996 2.00012C16.9996 1.17169 16.328 0.50012 15.4996 0.50012L1.9996 0.50012ZM14.6715 12.5507L3.06026 0.939459L0.938937 3.06078L12.5502 14.672L14.6715 12.5507Z"
            fill="#999999"
          />
        </svg>
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

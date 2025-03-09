/* eslint-disable react/prop-types */
// import ReaderViewIcon from "../../assets/ReaderView";
import ArrowIcon from "../../assets/InboxArrow";
import { color00, colorD9, colorTP, colorB0 } from "../../assets/constants";
import "./emailDisplay.css";
import "./emailEntry.css";
import "./emailList.css";

export default function Inbox({
  displaySummaries,
  emailList,
  setCurEmail,
  curEmail,
}) {
  return (
    <div className="inbox-display">
      <InboxEmailList
        displaySummaries={displaySummaries}
        emailList={emailList}
        curEmail={curEmail}
        onClick={setCurEmail}
      />
      <EmailDisplay key={curEmail} curEmail={curEmail} />
    </div>
  );
}

function EmailEntry({ displaySummary, email, onClick, selected }) {
  const colors = selected
    ? { main: colorD9, median: color00 }
    : { main: colorTP, median: colorB0 };
  const date = getDate(email.received_at);
  return (
    <div
      className={`entry${displaySummary ? "" : " no-summary"}`}
      style={{ backgroundColor: colors.main }}
      onClick={onClick}
    >
      <div className="indicator-container">
        <div className={!email.is_read && "indicator"}></div>
      </div>
      <div className="head">
        <div className="from">{getSenderName(email.sender)}</div>
        <div className="date">{date}</div>
      </div>
      <div className="title">{email.subject}</div>
      <div className="median-container">
        <div
          className="median"
          style={{ backgroundColor: colors.median }}
        ></div>
      </div>
      {displaySummary && <div className="summary">{email.summary_text}</div>}
    </div>
  );
}

function InboxEmailList({ displaySummaries, emailList, curEmail, onClick }) {
  const emails = () => {
    const returnBlock = [];
    for (const email of emailList) {
      returnBlock.push(
        <EmailEntry
          key={email.email_id}
          displaySummary={displaySummaries}
          email={email}
          onClick={() => onClick(email)}
          selected={email === curEmail}
        />
      );
    }
    return returnBlock;
  };
  return (
    <div className="list">
      <div className="inbox-title-container">
        <div className="inbox-title">
          <div className="inbox-icon">
            <ArrowIcon />
          </div>
          <div className="inbox-word">Inbox</div>
        </div>
      </div>
      <div className="divider"></div>
      <div className="email-container">
        <div className="emails">{emails()}</div>
      </div>
    </div>
  );
}

function EmailDisplay({ curEmail }) {
  const date = getDate(curEmail.received_at);
  return (
    <div className="email-display">
      <div className="header">
        <div className="from">{curEmail.sender}</div>
        <div className="title">{curEmail.subject}</div>
        <div className="to">{`To: ${curEmail.recipients}`}</div>
        <div className="date">{`Date: ${date}`}</div>
        <div className="reader-view">
          <ReaderView curEmail={curEmail} />
        </div>
      </div>
      <div className="body">
        <div className="content-container">
          <div className="content">{curEmail.body}</div>
        </div>
      </div>
    </div>
  );
}

// eslint-disable-next-line no-unused-vars
function ReaderView({ curEmail }) {
  return (
    <div>
      {/* <ReaderViewIcon /> */}
      <img src="./src/assets/oldAssets/ReaderView.svg" alt="ReaderView Icon" />
    </div>
  );
}

const getDate = (date) => {
  return `${date[1]}/${date[2]}/${date[0]}`;
};

const getSenderName = (sender) => {
  return sender.slice(0, sender.indexOf("<"));
};

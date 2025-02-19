/* eslint-disable react/prop-types */
import Icon from "../../assets/InboxArrow";
import "./emailDisplay.css";
import "./emailEntry.css";
import "./emailList.css";

export default function Inbox({ emailList, setCurEmail, curEmail }) {
  return (
    <div className="inbox-display">
      <InboxEmailList
        emailList={emailList}
        curEmail={curEmail}
        onClick={setCurEmail}
      />
      <EmailDisplay key={curEmail} curEmail={curEmail} />
    </div>
  );
}

function EmailEntry({ email, onClick, selected }) {
  const date = getDate(email.received_at);
  return (
    <div
      className="entry"
      style={{ backgroundColor: selected ? "#D9D9D9" : "transparent" }}
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
      <div className="separator-container">
        <div
          className="separator"
          style={{ backgroundColor: selected ? "#000000" : "#B0B0B0" }}
        ></div>
      </div>
      <div className="summary">{email.summary_text}</div>
    </div>
  );
}

function InboxEmailList({ emailList, curEmail, onClick }) {
  const emails = () => {
    const returnBlock = [];
    for (const email of emailList) {
      let selected = email === curEmail;
      returnBlock.push(
        <EmailEntry
          key={email.email_id}
          email={email}
          onClick={() => onClick(email)}
          selected={selected}
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
            <Icon />
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
      <img src="./src/assets/ReaderView.svg" alt="ReaderView Icon" />
    </div>
  );
}

const getDate = (date) => {
  return `${date[1]}/${date[2]}/${date[0]}`;
};

const getSenderName = (sender) => {
  return sender.slice(0, sender.indexOf("<"));
};

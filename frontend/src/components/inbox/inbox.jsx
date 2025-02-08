/* eslint-disable react/prop-types */
import "./emailDisplay.css";
import "./emailEntry.css";
import "./emailList.css";
import { useState } from "react";

export default function Inbox({ emailList }) {
  const [curEmail, setCurEmail] = useState(emailList[0]);
  const handleClick = (email) => {
    setCurEmail(emailList[email]);
  };
  return (
    <div className="inbox-display">
      <InboxEmailList
        emailList={emailList}
        curEmail={curEmail}
        onClick={handleClick}
      />
      <EmailDisplay key={curEmail} curEmail={curEmail} />
    </div>
  );
}

function EmailEntry({ email, onClick, selected }) {
  const brColor = selected ? "#D9D9D9" : "#FFFFFF";
  return (
    <div
      className="entry"
      style={{ backgroundColor: brColor }}
      onClick={onClick}
    >
      <div className="indicator-container">
        <div className="indicator"></div>
      </div>
      <div className="head">
        <div className="from">{email.from}</div>
        <div className="date">{email.date}</div>
      </div>
      <div className="title">{email.title}</div>
      <div className="separator-container">
        <div className="separator"></div>
      </div>
      <div className="summary">{email.summary}</div>
    </div>
  );
}

function InboxEmailList({ emailList, curEmail, onClick }) {
  const emails = () => {
    const returnBlock = [];
    for (let i = 0; i < 20; i++) {
      let selected = emailList[i] === curEmail;
      returnBlock.push(
        <EmailEntry
          key={i}
          email={emailList[i]}
          onClick={() => onClick(i)}
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
          <div className="inbox-icon">IN</div>
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
  return (
    <div className="email-display">
      <div className="header">
        <div className="from">{curEmail.from}</div>
        <div className="title">{curEmail.title}</div>
        <div className="to">{`To: ${curEmail.to}`}</div>
        <div className="date">{`Date: ${curEmail.date}`}</div>
        <ReaderView curEmail={curEmail} />
      </div>
      <div className="body">
        <div className="content-container">
          <div className="content">{curEmail.content}</div>
        </div>
      </div>
    </div>
  );
}

// eslint-disable-next-line no-unused-vars
function ReaderView({ curEmail }) {
  return <div></div>;
}

/* eslint-disable react/prop-types */
import "./emailEntry.css";
import "./emailList.css";
import {useState} from "react";

export default function Inbox() {
  const [curEmail, setCurEmail] = useState(0);
  const handleClick = email => {
    console.log(email);
    setCurEmail(email);
  };
  return (
    <div className="inbox-display">
      <InboxEmailList curEmail={curEmail} onClick={handleClick} />
      <EmailDisplay key={curEmail} curEmail={curEmail} />
    </div>
  );
}

function EmailEntry({onClick, selected}) {
  const brColor = selected ? "#000000" : "#FFFFFF";
  return (
    <div className="entry" style={{backgroundColor: brColor}} onClick={onClick}>
      <div className="indicator-container">
        <div className="indicator"></div>
      </div>
      <div className="head">
        <div className="from"></div>
        <div className="date"></div>
      </div>
      <div className="title"></div>
      <div className="separator-container">
        <div className="separator"></div>
      </div>
      <div className="summary"></div>
    </div>
  );
}

function InboxEmailList({curEmail, onClick}) {
  const emails = () => {
    const returnBlock = [];
    for (let i = 0; i < 25; i++) {
      let selected = i === curEmail;
      returnBlock.push(
        <EmailEntry key={i} onClick={() => onClick(i)} selected={selected} />
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

function EmailDisplay({key, curEmail}) {
  console.log(key);
  return (
    <div className="email-display">
      <ReaderView curEmail={curEmail} />
    </div>
  );
}

function ReaderView({curEmail}) {
  console.log(curEmail);
  return <div></div>;
}

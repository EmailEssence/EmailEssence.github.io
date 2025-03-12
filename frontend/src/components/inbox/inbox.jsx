/* eslint-disable react/prop-types */
// import ReaderViewIcon from "../../assets/ReaderView";
import ArrowIcon from "../../assets/InboxArrow";
import {
  color00,
  colorD9,
  colorTP,
  colorB0,
  emailsPerPage,
} from "../../assets/constants";
import { useState, useRef, useEffect } from "react";
import { Readability } from "@mozilla/readability";
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
        <div className={email.is_read ? "" : "indicator"}></div>
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
  const [pages, setPages] = useState(1);
  const ref = useRef(null);
  const maxEmails =
    pages * emailsPerPage < emailList.length
      ? pages * emailsPerPage
      : emailList.length;
  const hasUnloadedEmails = maxEmails < emailList.length;

  const handleScroll = () => {
    const fullyScrolled =
      Math.abs(
        ref.current.scrollHeight -
          ref.current.clientHeight -
          ref.current.scrollTop
      ) <= 1;
    if (fullyScrolled && hasUnloadedEmails) {
      setPages(pages + 1);
    }
  };

  useEffect(() => {
    handleScroll();
  }, [pages]); // Fixes minimum for large screens, but runs effect after every load which is unnecessary

  const emails = () => {
    const returnBlock = [];
    for (let i = 0; i < maxEmails; i++) {
      returnBlock.push(
        <EmailEntry
          key={emailList[i].email_id}
          displaySummary={displaySummaries}
          email={emailList[i]}
          onClick={() => onClick(emailList[i])}
          selected={emailList[i] === curEmail}
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
        <div className="emails" ref={ref} onScroll={handleScroll}>
          {emails()}
        </div>
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

function ReaderView({ curEmail }) {
  const [text, setText] = useState("Loading ...");
  const [displaying, setDisplaying] = useState(false);
  function displayReaderView() {
    if (!displaying) {
      const parser = new DOMParser();
      const doc = parser.parseFromString(curEmail.body, "text/html");
      const article = new Readability(doc).parse();
      setText(article.textContent);
    }
    setDisplaying(!displaying);
    console.log("display clicked");
  }
  useEffect(() => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(curEmail.body, "text/html");
    const article = new Readability(doc).parse();
    console.log(article.textContent);
  }, [curEmail]); // Inefficient way to do This
  return (
    <div onClick={displayReaderView}>
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

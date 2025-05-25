import PropTypes from "prop-types";
import { useEffect, useRef, useState } from "react";
import ArrowIcon from "../../../assets/InboxArrow";
import { emailsPerPage } from "../../../assets/constants";
import EmailDisplay from "./emailDisplay";
import { getPageSummaries } from "../../../emails/emailHandler";
import "./emailEntry.css";
import "./emailList.css";
import { trimList } from "../../../emails/emailHandler"; // shared API URL base

function Inbox({ displaySummaries, emailList, setCurEmail, curEmail }) {
  const [filteredEmails, setFilteredEmails] = useState(emailList);

  useEffect(() => {
    setFilteredEmails(emailList);
  }, [emailList]);

  const handleEmailSearch = (e) => {
    e === "" ? setFilteredEmails(emailList) : setFilteredEmails(trimList(e));
  };

  return (
    <div className="inbox-display">
      <InboxEmailList
        displaySummaries={displaySummaries}
        emailList={filteredEmails}
        curEmail={curEmail}
        onClick={setCurEmail}
        handleEmailSearch={handleEmailSearch}
      />
      <EmailDisplay key={curEmail?.email_id || "none"} curEmail={curEmail} />
    </div>
  );
}

function EmailEntry({ displaySummary, email, onClick, selected }) {
  const summary = () => {
    if (email.summary_text?.length > 0) {
      return <div className="summary">{email.summary_text}</div>;
    } else {
      return <div className="summary loading"></div>;
    }
  };

  const date = getDate(email.received_at);
  return (
    <div
      className={`entry${displaySummary ? "" : " no-summary"}${
        selected ? " selected" : ""
      }`}
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
        <div className="median"></div>
      </div>
      {displaySummary && summary()}
      <div className="email-median-container">
        <div className="median"></div>
      </div>
    </div>
  );
}

function InboxEmailList({
  displaySummaries,
  emailList,
  curEmail,
  onClick,
  handleEmailSearch,
}) {
  const [pages, setPages] = useState(1);
  const ref = useRef(null);
  const maxEmails = Math.min(pages * emailsPerPage, emailList.length);
  const hasUnloadedEmails = maxEmails < emailList.length;

  const handleScroll = () => {
    // add external summary call
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pages]); // Fixes minimum for large screens, but runs effect after every load which is unnecessary

  const emails = () => {
    const returnBlock = [];
    const needsSummary = [];
    for (let i = 0; i < maxEmails; i++) {
      if (displaySummaries && emailList[i].summary_text === "")
        needsSummary.push(emailList[i]);
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
    if (needsSummary.length > 0) getPageSummaries(needsSummary);
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

        <input
          type="text"
          placeholder="Search by keyword..."
          onChange={(e) => {
            handleEmailSearch(e.target.value);
            setPages(1);
          }}
          className="inbox-search"
        />
      </div>

      <div className="divider"></div>
      <div className="emails-wrapper">
        <div className="emails" ref={ref} onScroll={handleScroll}>
          {emails()}
          {emailList.length === 0 && (
            <div className="empty-results">No matching emails found.</div>
          )}
        </div>
      </div>
    </div>
  );
}

// PropTypes
Inbox.propTypes = {
  displaySummaries: PropTypes.bool,
  emailList: PropTypes.array,
  setCurEmail: PropTypes.func,
  curEmail: PropTypes.object,
};

EmailEntry.propTypes = {
  displaySummary: PropTypes.bool,
  email: PropTypes.object,
  onClick: PropTypes.func,
  selected: PropTypes.bool,
};

InboxEmailList.propTypes = {
  displaySummaries: PropTypes.bool,
  emailList: PropTypes.array,
  curEmail: PropTypes.object,
  onClick: PropTypes.func,
  handleEmailSearch: PropTypes.func,
};

// Utils
const getDate = (date) => `${date[1]}/${date[2]}/${date[0]}`;
const getSenderName = (sender) => sender.slice(0, sender.indexOf("<"));

export default Inbox;

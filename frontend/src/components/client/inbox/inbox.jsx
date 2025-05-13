import PropTypes from "prop-types";
import { useEffect, useRef, useState } from "react";
import ArrowIcon from "../../../assets/InboxArrow";
import { emailsPerPage } from "../../../assets/constants";
import EmailDisplay from "./emailDisplay";
import "./emailEntry.css";
import "./emailList.css";
import { baseUrl } from "../../../emails/emailHandler"; // shared API URL base

function Inbox({ displaySummaries, emailList, setCurEmail, curEmail }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredEmails, setFilteredEmails] = useState(emailList);
  const token = localStorage.getItem("auth_token");

  // sync filtered list when inbox updates
  useEffect(() => {
    setFilteredEmails(emailList);
  }, [emailList]);

  // handle keyword search input and call backend
  const handleSearch = async (e) => {
    const keyword = e.target.value;
    setSearchTerm(keyword);

    if (keyword.trim() === "") {
      setFilteredEmails(emailList);
      return;
    }

    console.log("Searching for:", keyword);
    console.log("Using token:", token);
    try {
      const res = await fetch(`${baseUrl}/emails/search?keyword=${keyword}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setFilteredEmails(data);
      } else {
        console.error("Search failed", res.status);
      }
    } catch (err) {
      console.error("Search error", err);
    }
  };

  return (
    <div className="inbox-display">
      {/* Search bar for filtering emails using summary keywords */}
      <div style={{ padding: "10px" }}>
        <input
          type="text"
          placeholder="Search by keyword..."
          value={searchTerm}
          onChange={handleSearch}
          style={{
            width: "100%",
            padding: "8px",
            fontSize: "14px",
            border: "1px solid #ccc",
            borderRadius: "4px",
          }}
        />
      </div>

      {/* Display email list filtered by searchTerm */}
      <InboxEmailList
        displaySummaries={displaySummaries}
        emailList={filteredEmails}
        curEmail={curEmail}
        onClick={setCurEmail}
      />
      <EmailDisplay key={curEmail?.email_id || "none"} curEmail={curEmail} />
    </div>
  );
}

function EmailEntry({ displaySummary, email, onClick, selected }) {
  const summary = () => {
    let returnBlock;
    if (email.summary_text.length > 0) {
      returnBlock = <div className="summary">{email.summary_text}</div>;
    } else {
      returnBlock = <div className="summary loading"></div>;
    }
    return returnBlock;
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
      <div className="emails" ref={ref} onScroll={handleScroll}>
        {emails()}
      </div>
    </div>
  );
}

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
};

const getDate = (date) => {
  return `${date[1]}/${date[2]}/${date[0]}`;
};

const getSenderName = (sender) => {
  return sender.slice(0, sender.indexOf("<"));
};

export default Inbox;

import PropTypes from "prop-types";
import { useEffect, useRef, useState } from "react";
import ArrowIcon from "../../../assets/InboxArrow";
import { emailsPerPage } from "../../../assets/constants";
import { getPageSummaries } from "../../../emails/emailHandler";
import EmailDisplay from "./emailDisplay";
import { trimList } from "../../../emails/emailHandler"; // shared API URL base
import "./emailEntry.css";
import "./emailList.css";

/**
 * Inbox component displays the email list and the selected email.
 * @param {Object} props
 * @param {boolean} props.displaySummaries - Whether to show summaries.
 * @param {Array<Email>} props.emailList - List of emails.
 * @param {Function} props.setCurEmail - Function to set the current email.
 * @param {Email} props.curEmail - The currently selected email.
 * @returns {JSX.Element}
 */

function Inbox({
  displaySummaries,
  emailList,
  setCurEmail,
  curEmail,
  requestMoreEmails,
  requestSummaries,
  hasUnloadedEmails,
  emailsPerPage,
}) {
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
        emailList={emailList}
        curEmail={curEmail}
        onClick={setCurEmail}
        handleEmailSearch={handleEmailSearch}
        requestMoreEmails={requestMoreEmails}
        requestSummaries={requestSummaries}
        hasUnloadedEmails={hasUnloadedEmails}
        emailsPerPage={emailsPerPage}
      />
      <EmailDisplay key={curEmail} curEmail={curEmail} />
    </div>
  );
}

/**
 * Renders a single email entry in the inbox list.
 * @param {Object} props
 * @param {boolean} props.displaySummary - Whether to show the summary.
 * @param {Email} props.email - The email object.
 * @param {Function} props.onClick - Function to select this email.
 * @param {boolean} props.selected - Whether this email is currently selected.
 * @returns {JSX.Element}
 */
function EmailEntry({ displaySummary, email, onClick, selected }) {
  /**
   * Renders the summary for the email, or a loading placeholder if not available.
   * @returns {JSX.Element}
   */
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
      <div className="email-median-container">
        <div className="median"></div>
      </div>
    </div>
  );
}

/**
 * Renders the list of emails in the inbox, with infinite scroll and summary fetching.
 * @param {Object} props
 * @param {boolean} props.displaySummaries - Whether to show summaries.
 * @param {Array<Email>} props.emailList - List of emails.
 * @param {Email} props.curEmail - The currently selected email.
 * @param {Function} props.onClick - Function to select an email.
 * @returns {JSX.Element}
 */
function InboxEmailList({
  displaySummaries,
  emailList,
  curEmail,
  onClick,
  handleEmailSearch,
  requestMoreEmails,
  requestSummaries,
  hasUnloadedEmails,
  emailsPerPage,
}) {
  // const [allEmailsLoaded, setAllEmailsLoaded] = useState(false);
  // const [loadingEmails, setLoadingEmails] = useState(false);
  const [pages, setPages] = useState(1);
  const ref = useRef(null);
  const maxEmails =
    pages * emailsPerPage < emailList.length
      ? pages * emailsPerPage
      : emailList.length;
  const hasLocallyUnloadedEmails = maxEmails < emailList.length;

  /**
   * Handles scroll event to load more emails when scrolled to the bottom.
   */
  const handleScroll = async () => {
    const fullyScrolled =
      Math.abs(
        
        ref.current.scrollHeight -
         
        ref.current.clientHeight -
         
        ref.current.scrollTop
      
      ) <= 1;
    if (fullyScrolled && (hasLocallyUnloadedEmails || hasUnloadedEmails)) {
      if (hasUnloadedEmails) {
        await requestMoreEmails();
      }
      setPages(pages + 1);
    }
  };

  useEffect(() => {
    handleScroll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pages]); // Fixes minimum for large screens, but runs effect after every load which is unnecessary

  /**
   * Renders the list of EmailEntry components up to maxEmails.
   * Fetches summaries for emails that need them.
   * @returns {JSX.Element[]}
   */
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
    if (needsSummary.length > 0) requestSummaries(needsSummary);
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
      <div className="emails" ref={ref} onScroll={handleScroll}>
        {emails()}
      </div>
    </div>
  );
}


const sharedPropTypes = {
  displaySummaries: PropTypes.bool,
  emailList: PropTypes.array,
  curEmail: PropTypes.object,
  requestMoreEmails: PropTypes.func,
  requestSummaries: PropTypes.func,
  hasUnloadedEmails: PropTypes.bool,
  emailsPerPage: PropTypes.number,
};
Inbox.propTypes = {
  ...sharedPropTypes,
  setCurEmail: PropTypes.func,
};

EmailEntry.propTypes = {
  displaySummary: PropTypes.bool,
  email: PropTypes.object,
  onClick: PropTypes.func,
  selected: PropTypes.bool,
};

InboxEmailList.propTypes = {
  ...sharedPropTypes,
  onClick: PropTypes.func,
  handleEmailSearch: PropTypes.func,
};

/**
 * Formats a date array as MM/DD/YYYY.
 * @param {Array<string|number>} date - [year, month, day]
 * @returns {string} Formatted date string.
 */
const getDate = (date) => `${date[1]}/${date[2]}/${date[0]}`;
const getSenderName = (sender) => sender.slice(0, sender.indexOf("<"));

export default Inbox;

/* eslint-disable react-hooks/exhaustive-deps */
import PropTypes from "prop-types";
import { useEffect, useRef, useState } from "react";
import FullScreenIcon from "../../../assets/FullScreenIcon";
import InboxIcon from "../../../assets/InboxArrow";
import { emailsPerPage } from "../../../assets/constants";
import "./miniview.css";

/**
 * MiniViewPanel component for the client dashboard.
 * Displays a list of emails in a compact view with an option to expand to the full inbox.
 * @param {Object} props
 * @param {Array<Email>} props.emailList - List of emails.
 * @param {Function} props.handlePageChange - Function to change the client page.
 * @param {Function} props.setCurEmail - Function to set the current email.
 * @returns {JSX.Element}
 */
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

/**
 * Renders the headfor the mini view
 * @param {Object} props
 * @param {Function} props.handlePageChange - Function to change the client page.
 * @returns {JSX.Element}
 */
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
        onClick={() => handlePageChange("/client/inbox")}
      >
        <FullScreenIcon />
      </div>
    </div>
  );
}

/**
 * Displays a scrollable list of emails, loading more as the user scrolls.
 * @param {Object} props
 * @param {Array<Email>} props.emailList - List of emails.
 * @param {Function} props.setCurEmail - Function to set the current email.
 * @param {Function} props.handlePageChange - Function to change the client page.
 * @returns {JSX.Element}
 */
function MiniViewBody({ emailList, setCurEmail, handlePageChange }) {
  const [pages, setPages] = useState(1);
  const ref = useRef(null);
  const maxEmails =
    pages * emailsPerPage < emailList.length
      ? pages * emailsPerPage
      : emailList.length;
  const hasUnloadedEmails = maxEmails < emailList.length;


  /**
   * Handles the scroll event to load more emails when the user scrolls to the bottom.
   */
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

  /**
 * Renders the list of MiniViewEmail components up to maxEmails.
 * @returns {JSX.Element[]}
 */
  const emails = () => {
    const returnBlock = [];
    for (let i = 0; i < maxEmails; i++) {
      returnBlock.push(
        <MiniViewEmail
          key={emailList[i].email_id}
          email={emailList[i]}
          setCurEmail={setCurEmail}
          handlePageChange={handlePageChange}
        />
      );
    }
    return returnBlock;
  };
  return (
    <div className="body-container" ref={ref} onScroll={handleScroll}>
      {emails()}
    </div>
  );
}

/**
 * Renders a single email entry in the mini view.
 * @param {Object} props
 * @param {Email} props.email - The email object.
 * @param {Function} props.setCurEmail - Function to set the current email.
 * @param {Function} props.handlePageChange - Function to change the client page.
 * @returns {JSX.Element}
 */
function MiniViewEmail({ email, setCurEmail, handlePageChange }) {
  return (
    <div
      className="miniview-email-container"
      onClick={() => {
        setCurEmail(email);
        handlePageChange("/client/inbox");
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

const commonPropTypesDashboard = {
  handlePageChange: PropTypes.func,
  setCurEmail: PropTypes.func,
};

MiniViewPanel.propTypes = {
  ...commonPropTypesDashboard,
  emailList: PropTypes.array,
};

MiniViewHead.propTypes = {
  handlePageChange: PropTypes.func,
};

MiniViewBody.propTypes = {
  ...commonPropTypesDashboard,
  emailList: PropTypes.array,
};

MiniViewEmail.propTypes = {
  ...commonPropTypesDashboard,
  email: PropTypes.object,
};

/**
 * Gets the sender's name from the sender string.
 * @param {string} sender - The sender string
 * @returns {string} The sender's name.
 */
const getSenderName = (sender) => {
  return sender.slice(0, sender.indexOf("<"));
};

export default MiniViewPanel;

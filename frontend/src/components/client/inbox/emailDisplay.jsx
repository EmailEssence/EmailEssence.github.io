import { Readability } from "@mozilla/readability";
import PropTypes from "prop-types";
import { useEffect, useState } from "react";
import ReactDom from "react-dom";
import ReaderViewIcon from "../../../assets/ReaderView";
import { getReaderView } from "../../../emails/emailHandler";
import Email from "./Email";
import "./emailDisplay.css";

/**
 * Displays the currently selected email with header, body, and reader view option.
 * @param {Object} props
 * @param {Email} props.curEmail - The currently selected email object.
 * @returns {JSX.Element}
 */
function EmailDisplay({
  curEmail = {
    user_id: 1,
    email_id: 1,
    sender: "",
    recipients: "",
    subject: "Test Subject",
    body: "",
    received_at: [0, 0, 0],
    summary_text: "",
  },
}) {
  const date = formatDate(curEmail.received_at);
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
          <Email email={curEmail} />
        </div>
      </div>
    </div>
  );
}

/**
 * Fetches and displays a simplified, readable version of the email.
 * @param {Object} props
 * @param {Email} props.curEmail - The currently selected email object.
 * @returns {JSX.Element}
 */
function ReaderView({ curEmail }) {
  const [text, setText] = useState("Loading ...");
  const [displaying, setDisplaying] = useState(false);

  /**
 * Toggles the display of the reader view and fetches content if opening.
 * @async
 * @returns {Promise<void>}
 */
  async function displayReaderView() {
    setDisplaying(!displaying);
    if (!displaying) {
      const readerViewText = await getReaderView(curEmail.email_id);
      const parser = new DOMParser();
      const doc = parser.parseFromString(readerViewText, "text/html");
      const article = new Readability(doc).parse();
      setText(article.textContent);
    }
  }

  useEffect(() => {
    setDisplaying(false);
    setText("Loading...");
  }, [curEmail]); // Inefficient way to clean state when email switches

  return (
    <div>
      <div
        className="icon-container"
        data-testid="reader-view-button"
        onClick={displayReaderView}
      >
        <ReaderViewIcon />
      </div>
      {displaying && (
        <PopUp
          isLoading={text === "Loading..."}
          handleClose={displayReaderView}
        >
          <div className="title">{curEmail.subject}</div>
          <div className="from">{`From: ${getSenderName(
            curEmail.sender
          )}`}</div>
          <div className="date">{formatDate(curEmail.received_at)}</div>
          <div className="gap"></div>
          <div className="body">{text}</div>
        </PopUp>
      )}
    </div>
  );
}

/**
 * Renders a modal overlay for displaying content or a loading spinner.
 * @param {Object} props
 * @param {boolean} props.isLoading - Whether to show the loading spinner.
 * @param {Function} props.handleClose - Function to close the popup.
 * @param {React.ReactNode} props.children - Content to display in the popup.
 * @returns {JSX.Element}
 */
function PopUp({ isLoading, handleClose, children }) {
  return ReactDom.createPortal(
    isLoading ? (
      <div className="loading-reader-view" onClick={handleClose}>
        <div className="loading-icon" data-testid="loading"></div>
      </div>
    ) : (
      <>
        <div className="overlay-background" />
        <div className="pop-up-container">
          <div className="content">{children}</div>
          <div className="button" onClick={handleClose}>
            Click To Close
          </div>
        </div>
      </>
    ),
    document.getElementById("portal")
  );
}

/**
 * Formats a date array as MM/DD/YYYY.
 * @param {Array<string|number>} date - [year, month, day]
 * @returns {string} Formatted date string.
 */
const formatDate = (date) => {
  return `${date[1]}/${date[2]}/${date[0]}`;
};

/**
 * Extracts the sender's name from the sender string.
 * @param {string} sender - The sender string
 * @returns {string} The sender's name.
 */
const getSenderName = (sender) => {
  return sender.slice(0, sender.indexOf("<"));
};

EmailDisplay.propTypes = {
  curEmail: PropTypes.object,
};

ReaderView.propTypes = {
  curEmail: PropTypes.object,
};

PopUp.propTypes = {
  isOpen: PropTypes.bool,
  handleClose: PropTypes.func,
  children: PropTypes.element,
};

export default EmailDisplay;

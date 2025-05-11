import { Readability } from "@mozilla/readability";
import PropTypes from "prop-types";
import { useEffect, useState } from "react";
import ReactDom from "react-dom";
import ReaderViewIcon from "../../../assets/ReaderView";
import Email from "./Email";
import { getReaderView } from "../../../emails/emailHandler";
import "./emailDisplay.css";

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

function ReaderView({ curEmail }) {
  const [text, setText] = useState("Loading ...");
  const [displaying, setDisplaying] = useState(false);

  async function displayReaderView() {
    if (!displaying) {
      const readerViewText = await getReaderView(curEmail.email_id);
      const parser = new DOMParser();
      const doc = parser.parseFromString(readerViewText, "text/html");
      const article = new Readability(doc).parse();
      setText(article.textContent);
    }
    setDisplaying(!displaying);
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
      <PopUp isOpen={displaying} handleClose={displayReaderView}>
        <div>{text}</div>
      </PopUp>
    </div>
  );
}

function PopUp({ isOpen, handleClose, children }) {
  if (!isOpen) return null;
  return ReactDom.createPortal(
    <>
      <div className="overlay-background" />
      <div className="pop-up-container">
        {children}
        <div className="button" onClick={handleClose}>
          Click To Close
        </div>
      </div>
    </>,
    document.getElementById("portal")
  );
}

const formatDate = (date) => {
  return `${date[1]}/${date[2]}/${date[0]}`;
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

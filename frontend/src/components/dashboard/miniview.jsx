/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useRef, useState } from "react";
import FullScreenIcon from "../../assets/FullScreenIcon";
import InboxIcon from "../../assets/InboxArrow";
import { emailsPerPage } from "../../assets/constants";
import PropTypes from "prop-types";
import "./miniview.css";

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
        onClick={() => handlePageChange("inbox")}
      >
        <FullScreenIcon />
      </div>
    </div>
  );
}

function MiniViewBody({ emailList, setCurEmail, handlePageChange }) {
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

function MiniViewEmail({ email, setCurEmail, handlePageChange }) {
  return (
    <div
      className="miniview-email-container"
      onClick={() => {
        setCurEmail(email);
        handlePageChange("inbox");
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

const getSenderName = (sender) => {
  return sender.slice(0, sender.indexOf("<"));
};

export default MiniViewPanel;

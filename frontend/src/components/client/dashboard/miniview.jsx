/* eslint-disable react-hooks/exhaustive-deps */
import PropTypes from "prop-types";
import { useEffect, useRef, useState } from "react";
import FullScreenIcon from "../../../assets/FullScreenIcon";
import InboxIcon from "../../../assets/InboxArrow";
import "./miniview.css";

function MiniViewPanel({
  emailList,
  handlePageChange,
  setCurEmail,
  requestMoreEmails,
  emailsPerPage,
  hasUnloadedEmails,
}) {
  return (
    <div className="mini-view">
      <MiniViewHead handlePageChange={handlePageChange} />
      <MiniViewBody
        emailList={emailList}
        setCurEmail={setCurEmail}
        handlePageChange={handlePageChange}
        requestMoreEmails={requestMoreEmails}
        emailsPerPage={emailsPerPage}
        hasUnloadedEmails={hasUnloadedEmails}
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
        onClick={() => handlePageChange("/client/inbox")}
      >
        <FullScreenIcon />
      </div>
    </div>
  );
}

function MiniViewBody({
  emailList,
  setCurEmail,
  handlePageChange,
  requestMoreEmails,
  emailsPerPage,
  hasUnloadedEmails,
}) {
  const [pages, setPages] = useState(1);
  const ref = useRef(null);
  let maxEmails = Math.min(pages * emailsPerPage, emailList.length);
  let hasLocallyUnloadedEmails = maxEmails < emailList.length;

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

const commonUtilityPropTypes = {
  emailList: PropTypes.array,
  requestMoreEmails: PropTypes.func,
  emailsPerPage: PropTypes.number,
  hasUnloadedEmails: PropTypes.bool,
};

MiniViewPanel.propTypes = {
  ...commonPropTypesDashboard,
  ...commonUtilityPropTypes,
};

MiniViewHead.propTypes = {
  handlePageChange: PropTypes.func,
};

MiniViewBody.propTypes = {
  ...commonPropTypesDashboard,
  ...commonUtilityPropTypes,
};

MiniViewEmail.propTypes = {
  ...commonPropTypesDashboard,
  email: PropTypes.object,
};

const getSenderName = (sender) => {
  return sender.slice(0, sender.indexOf("<"));
};

export default MiniViewPanel;

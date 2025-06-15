import { useEffect, useState } from "react";
import ViewIcon from "../../../assets/ViewIcon";
import { getTop5 } from "../../../emails/emailHandler";
import MiniViewPanel from "./miniview";
import PropTypes from "prop-types";
import "./dashboard.css";

function Dashboard({
  emailList,
  handlePageChange,
  setCurEmail,
  requestMoreEmails,
  emailsPerPage,
  requestSummaries,
  hasUnloadedEmails,
}) {
  return (
    <div className="dashboard">
      <WeightedEmailList
        emailList={emailList}
        setCurEmail={setCurEmail}
        handlePageChange={handlePageChange}
        requestSummaries={requestSummaries}
      />
      <MiniViewPanel
        emailList={emailList}
        handlePageChange={handlePageChange}
        setCurEmail={setCurEmail}
        requestMoreEmails={requestMoreEmails}
        emailsPerPage={emailsPerPage}
        hasUnloadedEmails={hasUnloadedEmails}
      />
    </div>
  );
}

function WeightedEmailList({
  emailList,
  setCurEmail,
  handlePageChange,
  requestSummaries,
}) {
  const [WEEmails, setWEEmails] = useState(startMiniView(emailList.length));

  useEffect(() => {
    async function fetchEmails() {
      const WEList = getTop5(emailList) || [];
      let needSummaries = WEList.filter(
        (email) => email.summary_text.length < 1 && email.keywords.length < 1
      );
      if (needSummaries.length > 0) await requestSummaries(needSummaries);
      setWEEmails(WEList);
    }
    fetchEmails();
  }, [emailList, requestSummaries]);
  return (
    <div className="weighted-email-list-container">
      {WEEmails.map((email) => {
        return (
          <WEListEmail
            key={email.email_id}
            email={email}
            setCurEmail={setCurEmail}
            handlePageChange={handlePageChange}
          />
        );
      })}
    </div>
  );
}

function WEListEmail({ email, setCurEmail, handlePageChange }) {
  const summary = () => {
    let returnBlock;
    if (email.summary_text.length > 0) {
      returnBlock = (
        <>
          <div className="summary">{email.summary_text}</div>
          <div
            className="email-link"
            data-testid={`WEListEmail${email.email_id}`}
            onClick={() => {
              setCurEmail(email); // Will not be reached when no email is present
              handlePageChange("/client/inbox");
            }}
          >
            <ViewIcon />
          </div>
        </>
      );
    } else {
      returnBlock = <div className="summary loading"></div>;
    }
    return returnBlock;
  };

  return (
    <div
      className={`welist-email-container ${
        email.summary_text.length > 0 ? "" : " solo"
      }`}
    >
      {summary()}
    </div>
  );
}

const commonPropTypesDashboard = {
  handlePageChange: PropTypes.func,
  setCurEmail: PropTypes.func,
};
Dashboard.propTypes = {
  ...commonPropTypesDashboard,
  emailList: PropTypes.array,
  requestMoreEmails: PropTypes.func,
  emailsPerPage: PropTypes.func,
  requestSummaries: PropTypes.func,
  hasUnloadedEmails: PropTypes.bool,
};

WeightedEmailList.propTypes = {
  ...commonPropTypesDashboard,
  emailList: PropTypes.array,
  requestSummaries: PropTypes.func,
};

WEListEmail.propTypes = {
  ...commonPropTypesDashboard,
  email: PropTypes.object,
};

const startMiniView = (size) => {
  let toReturn = [];
  for (let i = 0; i < Math.min(size, 5); i++) {
    toReturn.push({ email_id: i, summary_text: "" });
  }
  return toReturn;
};

export default Dashboard;

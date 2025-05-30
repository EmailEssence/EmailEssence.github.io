import ViewIcon from "../../../assets/ViewIcon";
import { getTop5 } from "../../../emails/emailHandler";
import MiniViewPanel from "./miniview";
import PropTypes from "prop-types";
import "./dashboard.css";

function Dashboard({ emailList, handlePageChange, setCurEmail }) {
  return (
    <div className="dashboard">
      <WeightedEmailList
        emailList={emailList}
        setCurEmail={setCurEmail}
        handlePageChange={handlePageChange}
      />
      <MiniViewPanel
        emailList={emailList}
        handlePageChange={handlePageChange}
        setCurEmail={setCurEmail}
      />
    </div>
  );
}

function WeightedEmailList({ emailList, setCurEmail, handlePageChange }) {
  const emails = () => {
    const WEList = getTop5(emailList);
    const returnBlock = [];
    for (let i = 0; i < WEList.length; i++) {
      returnBlock.push(
        <WEListEmail
          key={WEList[i].email_id}
          email={WEList[i]}
          setCurEmail={setCurEmail}
          handlePageChange={handlePageChange}
        />
      );
    }
    return returnBlock;
  };
  return <div className="weighted-email-list-container">{emails()}</div>;
}

function WEListEmail({ email, setCurEmail, handlePageChange }) {
  const summary = () => {
    let returnBlock;
    if (email.summary_text.length > 0) {
      returnBlock = <div className="summary">{email.summary_text}</div>;
    } else {
      returnBlock = <div className="summary loading"></div>;
    }
    return returnBlock;
  };

  return (
    <div className="welist-email-container">
      {summary()}
      <div
        className="email-link"
        data-testid={`WEListEmail${email.email_id}`}
        onClick={() => {
          setCurEmail(email);
          handlePageChange("/client/inbox");
        }}
      >
        <ViewIcon />
      </div>
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
};

WeightedEmailList.propTypes = {
  ...commonPropTypesDashboard,
  emailList: PropTypes.array,
};

WEListEmail.propTypes = {
  ...commonPropTypesDashboard,
  email: PropTypes.object,
};

export default Dashboard;

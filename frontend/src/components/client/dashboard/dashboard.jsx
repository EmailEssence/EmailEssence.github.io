import PropTypes from "prop-types";
import ViewIcon from "../../../assets/ViewIcon";
import { getTop5 } from "../../../emails/emailHandler";
import "./dashboard.css";
import MiniViewPanel from "./miniview";

/**
 * Dashboard component for the client.
 * Displays the weighted email list and the mini view panel.
 * @param {Object} props
 * @param {Array<Email>} props.emailList - List of emails.
 * @param {Function} props.handlePageChange - Function to change the client page.
 * @param {Function} props.setCurEmail - Function to set the current email.
 * @returns {JSX.Element}
 */
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

/**
 * Renders a list of the top 5 weighted emails.
 * @const {JSX.Element} WEList - Returns an array of WEListEmail components for the top 5 emails.
 * @param {Object} props
 * @param {Array<Email>} props.emailList - List of emails.
 * @param {Function} props.setCurEmail - Function to set the current email.
 * @param {Function} props.handlePageChange - Function to change the client page.
 * @returns {JSX.Element}
 */
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

/**
 * Renders a single weighted email entry with summary and view icon.
 * @const {JSX.Element} summary - Renders the summary for the email, or a loading placeholder if not available.
 * @param {Object} props
 * @param {Email} props.email - The email object.
 * @param {Function} props.setCurEmail - Function to set the current email.
 * @param {Function} props.handlePageChange - Function to change the client page.
 * @returns {JSX.Element}
 */
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

import PropTypes from "prop-types";

/**
 * Renders the email body, using inner HTML if present.
 * @param {Object} props
 * @param {Email} props.email - The email object to display.
 * @returns {JSX.Element}
 */
export function Email({ email }) {
  return (
    <>
      {email.hasInnerHTML ? (
        <div
          className="content"
          dangerouslySetInnerHTML={{ __html: email.body }}
        ></div>
      ) : (
        <div className="content">{email.body}</div>
      )}
    </>
  );
}

Email.propTypes = {
  email: PropTypes.object,
};

export default Email;

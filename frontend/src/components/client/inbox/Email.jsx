import PropTypes from "prop-types";

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

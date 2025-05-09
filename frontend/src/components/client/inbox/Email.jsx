import PropTypes from "prop-types";

export function Email({ email }) {
  return (
    <div
      className="content"
      dangerouslySetInnerHTML={{ __html: email.body }}
    ></div>
  );
}

Email.propTypes = {
  email: PropTypes.object,
};

export default Email;

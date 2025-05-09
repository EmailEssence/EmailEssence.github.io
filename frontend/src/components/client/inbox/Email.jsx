import PropTypes from "prop-types";

export function Email({ content }) {
  return <>{content}</>;
}

Email.propTypes = {
  content: PropTypes.string,
};

export default Email;

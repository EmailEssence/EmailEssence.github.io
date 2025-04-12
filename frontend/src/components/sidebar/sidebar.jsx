import InboxIcon from "../../assets/InboxIcon";
import Logo from "../../assets/Logo";
import SettingsIcon from "../../assets/SettingsIcon";
import PropTypes from "prop-types";
import DashboardIcon from "../../assets/DashboardIcon";
import { useLocation } from "react-router";
import "./sidebar.css";

function SideBar({ onLogoClick, expanded, handlePageChange }) {
  const location = useLocation();
  const route = location.pathname;
  return (
    <div className="sidebar" data-testid="sidebar">
      <Button expanded={expanded} onClick={onLogoClick} name="logo">
        <Logo />
      </Button>
      <Button
        expanded={expanded}
        curState={route}
        onClick={() => handlePageChange("/client/dashboard")}
        name="dashboard"
      >
        <DashboardIcon />
      </Button>
      <Button
        expanded={expanded}
        curState={route}
        onClick={() => handlePageChange("/client/inbox")}
        name="inbox"
      >
        <InboxIcon />
      </Button>
      <div></div>
      <Button
        expanded={expanded}
        curState={route}
        onClick={() => handlePageChange("/client/settings")}
        name="settings"
      >
        <SettingsIcon />
      </Button>
    </div>
  );
}

function Button({ expanded, curState = "None", onClick, name, children }) {
  const text =
    name === "logo" ? "" : `${name[0].toUpperCase()}${name.slice(1)}`;
  const selectedClass = curState.includes(name) ? " selected" : "";
  return (
    <div
      className={`container${selectedClass}`}
      onClick={onClick}
      role="button"
      aria-pressed="false"
      data-testid={name}
    >
      <div className="icon">
        <div className={name === "logo" && "logo"}>{children}</div>
        {expanded && <p>{text}</p>}
      </div>
    </div>
  );
}

Button.propTypes = {
  expanded: PropTypes.bool,
  curState: PropTypes.string,
  onClick: PropTypes.func,
  name: PropTypes.string,
  children: PropTypes.element,
};
SideBar.propTypes = {
  onLogoClick: PropTypes.func,
  expanded: PropTypes.bool,
  handlePageChange: PropTypes.func,
  selected: PropTypes.string,
};

export default SideBar;

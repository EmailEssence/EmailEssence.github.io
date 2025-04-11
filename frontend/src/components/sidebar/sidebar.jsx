import InboxIcon from "../../assets/InboxIcon";
import Logo from "../../assets/Logo";
import SettingsIcon from "../../assets/SettingsIcon";
import PropTypes from "prop-types";
import DashboardIcon from "../../assets/DashboardIcon";
import "./sidebar.css";

function SideBar({ onLogoClick, expanded, handlePageChange, selected }) {
  return (
    <div className="sidebar" data-testid="sidebar">
      <Button expanded={expanded} onClick={onLogoClick} name="">
        <Logo />
      </Button>
      <Button
        expanded={expanded}
        curState={selected}
        onClick={() => handlePageChange("/client/dashboard")}
      >
        <DashboardIcon />
      </Button>
      <Button
        expanded={expanded}
        curState={selected}
        onClick={() => handlePageChange("/client/inbox")}
        name="inbox"
      >
        <InboxIcon />
      </Button>
      <div></div>
      <Button
        expanded={expanded}
        curState={selected}
        onClick={() => handlePageChange("/client/settings")}
        name="settings"
      >
        <SettingsIcon />
      </Button>
    </div>
  );
}

function Button({ expanded, curState = "N", onClick, name, children }) {
  const text =
    name.length > 0 ? `${name[0].toUpperCase()}${name.slice(1)}` : "";
  const selectedClass = curState === name ? " selected" : "";
  return (
    <div
      className={`container${selectedClass}`}
      onClick={onClick}
      role="button"
      aria-pressed="false"
      data-testid={name.length > 0 ? name : "logo"}
    >
      <div className="icon">
        <div className={text.length < 1 ? "logo" : ""}>{children}</div>
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

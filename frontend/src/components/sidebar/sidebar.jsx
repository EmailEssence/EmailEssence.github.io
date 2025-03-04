/* eslint-disable react/prop-types */
import { color1E, colorD9, colorE9 } from "../../assets/constants";
import InboxIcon from "../../assets/InboxIcon";
import SettingsIcon from "../../assets/SettingsIcon";
// import Logo from "../../assets/Logo";
import "./sidebar.css";

export default function SideBar({
  onLogoClick,
  expanded,
  handlePageChange,
  selected,
}) {
  return (
    <div>
      <div className="sidebar">
        <Button expanded={expanded} onClick={onLogoClick} name="">
          {/* <Logo /> */}
          <img src="./src/assets/oldAssets/Logo.svg" alt="Logo Icon" />
        </Button>
        <Button
          expanded={expanded}
          curState={selected}
          onClick={() => handlePageChange("inbox")}
          name="inbox"
        >
          <InboxIcon color={selected === "inbox" ? color1E : colorE9} />
        </Button>
        <div></div>
        <Button
          expanded={expanded}
          curState={selected}
          onClick={() => handlePageChange("settings")}
          name="settings"
        >
          <SettingsIcon color={selected === "settings" ? color1E : colorE9} />
        </Button>
      </div>
    </div>
  );
}

function Button({ expanded, curState = "N", onClick, name, children }) {
  const text =
    name.length > 0 ? `${name[0].toUpperCase()}${name.slice(1)}` : "";
  const colors =
    curState === name
      ? { main: colorD9, sub: color1E }
      : { main: color1E, sub: colorE9 };
  return (
    <div>
      <div
        className="container"
        onClick={onClick}
        style={{
          backgroundColor: colors.main,
        }}
      >
        <div className="icon">
          <div>{children}</div>
          {expanded && <p style={{ color: colors.sub }}>{text}</p>}
        </div>
      </div>
    </div>
  );
}

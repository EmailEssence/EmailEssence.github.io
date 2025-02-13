/* eslint-disable react/prop-types */
import { color1E, colorD9, colorE9 } from "../../assets/constants";
import InboxIcon from "../../assets/InboxIcon";
import SettingsIcon from "../../assets/SettingsIcon";
import "./sidebar.css";

export default function SideBar({
  onLogoClick,
  containerWidth,
  handlePageChange,
  selected,
}) {
  return (
    <div>
      <div className="sidebar" style={{ width: containerWidth }}>
        <Button containerWidth={containerWidth} onClick={onLogoClick} name="">
          <img src="./src/assets/Logo.svg" alt="Login Icon" />
        </Button>
        <Button
          containerWidth={containerWidth}
          curState={selected}
          onClick={() => handlePageChange("inbox")}
          name="inbox"
        >
          <InboxIcon color={selected === "inbox" ? color1E : colorE9} />
        </Button>
        <div></div>
        <Button
          containerWidth={containerWidth}
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

function Button({ containerWidth, curState = "N", onClick, name, children }) {
  const buttonText =
    name.length > 0 ? `${name[0].toUpperCase()}${name.slice(1)}` : "";
  const text = containerWidth === "80px" ? "" : buttonText;
  const color = curState === name ? colorD9 : color1E;
  const eColor = curState === name ? color1E : colorE9;
  return (
    <div>
      <div
        className="container"
        onClick={onClick}
        style={{
          backgroundColor: color,
          width: containerWidth,
        }}
      >
        <div className="icon">
          <div>{children}</div>
          <p style={{ color: eColor }}>{text}</p>
        </div>
      </div>
    </div>
  );
}

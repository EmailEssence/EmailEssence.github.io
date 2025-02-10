/* eslint-disable react/prop-types */
import { color1E, colorD9, colorE9 } from "../../assets/constants";
import InboxIcon from "../../assets/InboxIcon";
import SettingsIcon from "../../assets/SettingsIcon";
import "./sidebar.css";

export default function SideBar({
  onLogoClick,
  containerWidth,
  getPageComponent,
  selected,
}) {
  return (
    <div>
      <div className="sidebar" style={{ width: containerWidth }}>
        <LogoButton
          containerWidth={containerWidth}
          curState={selected}
          onClick={() => {
            onLogoClick();
          }}
        />
        <Button
          containerWidth={containerWidth}
          curState={selected}
          onClick={() => getPageComponent("inbox")}
          name="inbox"
        >
          <InboxIcon color={selected === "inbox" ? color1E : colorE9} />
        </Button>
        <div></div>
        <Button
          containerWidth={containerWidth}
          curState={selected}
          onClick={() => getPageComponent("settings")}
          name="settings"
        >
          <SettingsIcon color={selected === "settings" ? color1E : colorE9} />
        </Button>
      </div>
    </div>
  );
}

function LogoButton({ containerWidth, onClick }) {
  return (
    <div>
      <div
        className="container"
        id="dashboard"
        onClick={onClick}
        style={{
          backgroundColor: color1E,
          width: containerWidth,
        }}
      >
        <p>EmailESSENCE</p>
      </div>
    </div>
  );
}

function Button({ containerWidth, curState, onClick, name, children }) {
  const buttonText = `${name[0].toUpperCase()}${name.slice(1)}`;
  const text = containerWidth === "80px" ? "" : buttonText;
  const color = curState === name ? colorD9 : color1E;
  const eColor = curState === name ? color1E : colorE9;
  return (
    <div>
      <div
        className="container"
        id={name}
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

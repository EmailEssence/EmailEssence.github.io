/* eslint-disable react/prop-types */
import InboxIcon from "../../assets/InboxIcon";
import SettingsIcon from "../../assets/SettingsIcon";
import "./sidebar.css";

const unselectedColor = "#1E1E1E";
const selectedColor = "#D9D9D9";
const unselectedColorInner = "#E9E9E9";
const selectedColorInner = "#1E1E1E";
const sideBarContracted = "80px";

export default function SideBar({
  onLogoClick,
  containerWidth,
  getPageComponent,
  selected,
}) {
  return (
    <div>
      <div className="sidebar" style={{width: containerWidth}}>
        <LogoButton
          containerWidth={containerWidth}
          curState={selected}
          onClick={() => {
            getPageComponent("dashboard");
            onLogoClick();
          }}
        />
        <InboxButton
          containerWidth={containerWidth}
          curState={selected}
          onClick={() => getPageComponent("inbox")}
        />
        <p></p>
        <SettingsButton
          containerWidth={containerWidth}
          curState={selected}
          onClick={() => getPageComponent("settings")}
        />
      </div>
    </div>
  );
}

function LogoButton({containerWidth, curState, onClick}) {
  const color = curState === "dashboard" ? selectedColor : unselectedColor;
  return (
    <div>
      <div
        className="container"
        id="dashboard"
        onClick={onClick}
        style={{
          backgroundColor: color,
          width: containerWidth,
        }}
      >
        <p>EmailESSENCE</p>
      </div>
    </div>
  );
}

function InboxButton({containerWidth, curState, onClick}) {
  const text = containerWidth === sideBarContracted ? "" : "Inbox";
  const color = curState === "inbox" ? selectedColor : unselectedColor;
  const innerColor =
    curState === "inbox" ? selectedColorInner : unselectedColorInner;
  return (
    <div>
      <div
        className="container"
        id="inbox"
        onClick={onClick}
        style={{backgroundColor: color, width: containerWidth}}
      >
        <div className="icon">
          <div>
            <InboxIcon color={innerColor} />
          </div>
          <p style={{color: innerColor}}>{text}</p>
        </div>
      </div>
    </div>
  );
}

function SettingsButton({containerWidth, curState, onClick}) {
  const text = containerWidth === sideBarContracted ? "" : "Settings";
  const color = curState === "settings" ? selectedColor : unselectedColor;
  const innerColor =
    curState === "settings" ? selectedColorInner : unselectedColorInner;
  return (
    <div>
      <div
        className="container"
        id="settings"
        onClick={onClick}
        style={{
          backgroundColor: color,
          width: containerWidth,
        }}
      >
        <div className="icon">
          <div>
            <SettingsIcon color={innerColor} />
          </div>
          <p style={{color: innerColor}}>{text}</p>
        </div>
      </div>
    </div>
  );
}

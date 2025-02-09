/* eslint-disable react/prop-types */
import InboxIcon from "../../assets/InboxIcon";
import SettingsIcon from "../../assets/SettingsIcon";
import "./sidebar.css";

const unselectedColor = "#1E1E1E";
const selectedColor = "#D9D9D9";
const eColorSelected = "#E9E9E9";
const eColorUnselected = "#1E1E1E";

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
            getPageComponent("dashboard");
            onLogoClick();
          }}
        />
        <Button
          containerWidth={containerWidth}
          curState={selected}
          onClick={() => getPageComponent("inbox")}
          name="inbox"
        >
          <InboxIcon
            color={selected === "inbox" ? eColorSelected : eColorUnselected}
          />
        </Button>
        <div></div>
        <Button
          containerWidth={containerWidth}
          curState={selected}
          onClick={() => getPageComponent("settings")}
          name="settings"
        >
          <SettingsIcon
            color={selected === "settings" ? eColorSelected : eColorUnselected}
          />
        </Button>
      </div>
    </div>
  );
}

function LogoButton({ containerWidth, curState, onClick }) {
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

function Button({ containerWidth, curState, onClick, name, children }) {
  const buttonText = `${name[0].toUpperCase()}${name.slice(1)}`;
  const text = containerWidth === "80px" ? "" : buttonText;
  const color = curState === name ? selectedColor : unselectedColor;
  const eColor = curState === name ? eColorSelected : eColorUnselected;
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

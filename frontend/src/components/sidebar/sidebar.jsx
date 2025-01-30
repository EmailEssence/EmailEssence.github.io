import "./sidebar.css";
import {useState} from "react";
import SettingsIcon from "../../assets/SettingsIcon";
import InboxIcon from "../../assets/InboxIcon";

const unselectedColor = "#1E1E1E";
const selectedColor = "#D9D9D9";

export default function SideBar() {
  const [selected, setSelected] = useState("logo");
  const [containerWidth, setContainerWidth] = useState("80px");

  const handleClick = useStateID => {
    //expands the sidebar when the logo is clicked
    if (useStateID === "logo") {
      containerWidth === "80px"
        ? setContainerWidth("180px")
        : setContainerWidth("80px");
    }

    //sets the selected state ID to dashboard after being unselected
    if (selected === useStateID) {
      setSelected("logo");
      return;
    }
    setSelected(useStateID);
  };

  return (
    <div>
      <div className="sidebar" style={{width: containerWidth}}>
        <LogoButton
          containerWidth={containerWidth}
          curState={selected}
          onClick={() => handleClick("logo")}
        />
        <InboxButton
          containerWidth={containerWidth}
          curState={selected}
          onClick={() => handleClick("inbox")}
        />
        <p></p>
        <SettingsButton
          containerWidth={containerWidth}
          curState={selected}
          onClick={() => handleClick("settings")}
        />
      </div>
    </div>
  );
}

// eslint-disable-next-line react/prop-types
function LogoButton({containerWidth, curState, onClick}) {
  const color = curState === "logo" ? selectedColor : unselectedColor;
  return (
    <div>
      <button
        className="container"
        id="logo"
        onClick={onClick}
        style={{
          backgroundColor: color,
          width: containerWidth,
        }}
      >
        <p>EmailESSENCE</p>
      </button>
    </div>
  );
}

// eslint-disable-next-line react/prop-types
function InboxButton({containerWidth, curState, onClick}) {
  const color = curState === "inbox" ? selectedColor : unselectedColor;
  return (
    <div>
      <button
        className="container"
        id="inbox"
        onClick={onClick}
        style={{backgroundColor: color, width: containerWidth}}
      >
        <InboxIcon className="icon" />
      </button>
    </div>
  );
}

// eslint-disable-next-line react/prop-types
function SettingsButton({containerWidth, curState, onClick}) {
  const color = curState === "settings" ? selectedColor : unselectedColor;
  return (
    <div>
      <button
        className="container"
        id="settings"
        onClick={onClick}
        style={{
          backgroundColor: color,
          width: containerWidth,
        }}
      >
        <SettingsIcon className="icon" />
      </button>
    </div>
  );
}

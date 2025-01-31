import React, { useState } from "react";
import "./settings.css";

export default function Settings() {
    return (
        <div className="settings">
            <h1>Settings</h1>
            <SummariesInInbox />
            <EmailFetchInterval />
            <Theme />
        </div>
    );
}

function SummariesInInbox() {
    const [isChecked, setIsChecked] = useState(false);
    const handleToggle = () => setIsChecked(!isChecked);

    return (
        <div className="settings-block">
            <h2>Summaries in Inbox</h2>
            <label className="switch">
                <input type="checkbox" checked={isChecked} onChange={handleToggle}/>
                <span className="slider"></span>
            </label>
        </div>
    );
}

function EmailFetchInterval() {
    return (
        <div className="settings-block">
            <h2>Email Fetch Interval</h2>
            <input
                type="range"
                min="5"
                max="600"
                step="1"
                onInput={(inputEvent) => inputEvent.target.nextSibling.textContent = `${inputEvent.target.value} seconds`}
            />
            <p>5 seconds</p>
        </div>
    );
}


function Theme() {
    const [theme, setTheme] = useState("system");

    return (
        <div className="settings-block">
            <h2>Theme</h2>
            <div className="theme">
                
            </div>
        </div>
    );
}

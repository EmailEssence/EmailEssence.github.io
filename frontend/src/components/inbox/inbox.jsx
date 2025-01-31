import "./inbox.css";

export default function Inbox() {
  return (
    <div>
      <InboxEmailList />
      <EmailDisplay />
    </div>
  );
}

function EmailEntry() {
  return (
    <div className="entry">
      <div className="indicator-container">
        <div className="indicator"></div>
      </div>
      <div className="head">
        <div className="from"></div>
        <div className="date"></div>
      </div>
      <div className="title"></div>
      <div className="separator-container">
        <div className="seperator"></div>
      </div>
      <div className="summary"></div>
    </div>
  );
}

function InboxEmailList() {
  return <EmailEntry />;
}

function EmailDisplay() {
  return <ReaderView />;
}

function ReaderView() {
  return <div></div>;
}

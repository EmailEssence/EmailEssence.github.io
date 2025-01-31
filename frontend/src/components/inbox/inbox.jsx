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
        <div className="separator"></div>
      </div>
      <div className="summary"></div>
    </div>
  );
}

function InboxEmailList() {
  return (
    <div>
      <div className="inbox-title">
        <div className="inbox-word"></div>
      </div>
      <div className="email-list">
        <EmailEntry />
      </div>
      <div className="scrollbar-container">
        <div className="scrollbar">
          <div className="nub"></div>
        </div>
      </div>
    </div>
  );
}

function EmailDisplay() {
  return <ReaderView />;
}

function ReaderView() {
  return <div></div>;
}

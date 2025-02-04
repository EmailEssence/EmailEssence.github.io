import "./emailEntry.css";
import "./emailList.css";

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
  const emails = () => {
    const returnBlock = [];
    for (let i = 0; i < 25; i++) {
      returnBlock.push(<EmailEntry key={i} />);
    }
    return returnBlock;
  };
  return (
    <div className="list">
      <div className="inbox-title-container">
        <div className="inbox-title">
          <div className="inbox-icon">IN</div>
          <div className="inbox-word">Inbox</div>
        </div>
      </div>
      <div className="divider"></div>
      <div className="email-container">
        <div className="emails">{emails()}</div>
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

export default function Inbox() {
  return (
    <div>
      <InboxEmailList />
      <EmailDisplay />
    </div>
  );
}

function EmailEntry() {
  return <div></div>;
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

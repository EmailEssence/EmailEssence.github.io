import "./Loading.css";

export default function Loading() {
  return (
    <div className="loading">
      <div className="loading-spinner" role="spinner"></div>
      <p className="loading-text">Loading...</p>
    </div>
  );
}

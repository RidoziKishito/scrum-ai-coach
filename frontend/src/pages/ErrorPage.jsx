import { Link, useLocation } from "react-router-dom";
import "./ErrorPage.css";

const PAGE_CONTENT = {
  unauthorized: {
    code: "401",
    title: "Sign in required",
    message: "Your session is missing or has expired. Sign in again to continue.",
    primaryLabel: "Go to login",
    primaryTo: "/login",
    secondaryLabel: "Back to welcome",
    secondaryTo: "/welcome",
  },
  forbidden: {
    code: "403",
    title: "Access unavailable",
    message: "This page is not available for your current account setup.",
    primaryLabel: "Complete onboarding",
    primaryTo: "/onboarding",
    secondaryLabel: "Go to dashboard",
    secondaryTo: "/dashboard",
  },
  notFound: {
    code: "404",
    title: "Page not found",
    message: "The page you are looking for does not exist or may have been moved.",
    primaryLabel: "Go to dashboard",
    primaryTo: "/dashboard",
    secondaryLabel: "Back to welcome",
    secondaryTo: "/welcome",
  },
};

export default function ErrorPage({ type = "notFound" }) {
  const location = useLocation();
  const content = PAGE_CONTENT[type] || PAGE_CONTENT.notFound;
  const from = location.state?.from?.pathname;
  const primaryTo = type === "unauthorized" && from
    ? `${content.primaryTo}?next=${encodeURIComponent(from)}`
    : content.primaryTo;

  return (
    <section className="error-page">
      <div className="error-panel">
        <span className="error-code">{content.code}</span>
        <h1>{content.title}</h1>
        <p>{content.message}</p>
        <div className="error-actions">
          <Link className="error-primary-action" to={primaryTo}>
            {content.primaryLabel}
          </Link>
          <Link className="error-secondary-action" to={content.secondaryTo}>
            {content.secondaryLabel}
          </Link>
        </div>
      </div>
    </section>
  );
}

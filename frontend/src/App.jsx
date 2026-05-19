import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import SkillAssessment from "./pages/SkillAssessment";

const initialForm = {
  email: "",
  password: ""
};

const shellStyle = {
  minHeight: "100vh",
  display: "grid",
  placeItems: "center",
  padding: "24px",
  fontFamily: '"Segoe UI", "Helvetica Neue", sans-serif',
  background:
    "radial-gradient(circle at top left, #f7c98b 0%, rgba(247, 201, 139, 0) 28%), radial-gradient(circle at bottom right, #b7dfc8 0%, rgba(183, 223, 200, 0) 32%), linear-gradient(135deg, #f7f2e9 0%, #e8efe6 100%)",
  color: "#203127"
};

const cardStyle = {
  width: "100%",
  maxWidth: "440px",
  padding: "32px",
  borderRadius: "28px",
  background: "rgba(255, 252, 247, 0.86)",
  border: "1px solid rgba(24, 37, 28, 0.12)",
  boxShadow: "0 24px 60px rgba(41, 54, 47, 0.16)",
  backdropFilter: "blur(18px)"
};

const fieldStyle = {
  width: "100%",
  padding: "14px 16px",
  borderRadius: "16px",
  border: "1px solid rgba(29, 43, 35, 0.16)",
  background: "rgba(255, 255, 255, 0.82)",
  color: "#203127",
  fontSize: "15px",
  outline: "none",
  boxSizing: "border-box"
};

function RegisterPage() {
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [serverError, setServerError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const updateField = (key, value) => {
    setForm((current) => ({
      ...current,
      [key]: value
    }));
  };

  const validateForm = () => {
    const nextErrors = {};

    if (!form.email.trim()) {
      nextErrors.email = "Please enter your email address.";
    } else if (!/^\S+@\S+\.\S+$/.test(form.email)) {
      nextErrors.email = "Please enter a valid email address.";
    }

    if (!form.password) {
      nextErrors.password = "Please enter your password.";
    }

    return nextErrors;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const nextErrors = validateForm();
    setErrors(nextErrors);
    setServerError("");
    setSuccessMessage("");

    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email: form.email,
          password: form.password
        })
      });

      const result = await response.json().catch(() => null);

      if (!response.ok) {
        setServerError(
          result?.message ||
          result?.detail ||
          "Registration failed. Please try again."
        );
        return;
      }

      setSuccessMessage("Registration successful. Redirecting to onboarding...");

      window.setTimeout(() => {
        window.location.href = "/assess-skills";
      }, 1200);
    } catch (error) {
      setServerError("Cannot connect to the server right now.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={shellStyle}>
      <section style={cardStyle}>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "8px 14px",
            borderRadius: "999px",
            background: "#21352a",
            color: "#fff9f1",
            fontSize: "13px",
            letterSpacing: "0.04em",
            textTransform: "uppercase"
          }}
        >
          Scrum AI Coach
        </div>

        <h1
          style={{
            margin: "20px 0 10px",
            fontSize: "clamp(2rem, 4vw, 2.8rem)",
            lineHeight: 1.05,
            letterSpacing: "-0.04em"
          }}
        >
          Register
        </h1>

        <p
          style={{
            margin: "0 0 24px",
            lineHeight: 1.6,
            color: "rgba(32, 49, 39, 0.72)"
          }}
        >
          Create your account to continue to the onboarding and skill assessment flow.
        </p>

        <form onSubmit={handleSubmit}>
          <div style={{ display: "grid", gap: "16px" }}>
            <label>
              <span style={{ display: "block", marginBottom: "8px", fontWeight: 600 }}>
                Email
              </span>
              <input
                type="email"
                value={form.email}
                onChange={(event) => updateField("email", event.target.value)}
                placeholder="you@example.com"
                style={fieldStyle}
              />
              {errors.email && (
                <span style={{ display: "block", marginTop: "6px", color: "#b3481f" }}>
                  {errors.email}
                </span>
              )}
            </label>

            <label>
              <span style={{ display: "block", marginBottom: "8px", fontWeight: 600 }}>
                Password
              </span>
              <input
                type="password"
                value={form.password}
                onChange={(event) => updateField("password", event.target.value)}
                placeholder="Enter your password"
                style={fieldStyle}
              />
              {errors.password && (
                <span style={{ display: "block", marginTop: "6px", color: "#b3481f" }}>
                  {errors.password}
                </span>
              )}
            </label>
          </div>

          {serverError && (
            <div
              style={{
                marginTop: "14px",
                padding: "12px 14px",
                borderRadius: "14px",
                background: "rgba(179, 72, 31, 0.12)",
                border: "1px solid rgba(179, 72, 31, 0.18)",
                color: "#8f3415"
              }}
            >
              {serverError}
            </div>
          )}

          {successMessage && (
            <div
              style={{
                marginTop: "14px",
                padding: "12px 14px",
                borderRadius: "14px",
                background: "rgba(49, 122, 82, 0.12)",
                border: "1px solid rgba(49, 122, 82, 0.18)",
                color: "#1f6b45"
              }}
            >
              {successMessage}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: "100%",
              marginTop: "22px",
              padding: "14px 22px",
              borderRadius: "16px",
              border: "none",
              background: "#203127",
              color: "#fff8ef",
              fontSize: "15px",
              fontWeight: 700,
              cursor: "pointer"
            }}
          >
            {isSubmitting ? "Registering..." : "Register"}
          </button>
        </form>
      </section>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RegisterPage />} />
        <Route
          path="/assess-skills"
          element={
            <Layout>
              <SkillAssessment />
            </Layout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

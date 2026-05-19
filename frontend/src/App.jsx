import { useState } from "react";

const initialForm = {
  fullName: "",
  email: "",
  password: "",
  confirmPassword: "",
  role: "Developer",
  experience: "0-1 years",
  learningFocus: "Agile foundations",
  teamName: "",
  agreeToTerms: false
};

const cardStyle = {
  background: "rgba(255, 252, 247, 0.84)",
  border: "1px solid rgba(24, 37, 28, 0.12)",
  borderRadius: "28px",
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

function App() {
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [registeredUser, setRegisteredUser] = useState(null);

  const updateField = (key, value) => {
    setForm((current) => ({
      ...current,
      [key]: value
    }));
  };

  const validateForm = () => {
    const nextErrors = {};

    if (!form.fullName.trim()) {
      nextErrors.fullName = "Please enter your full name.";
    }

    if (!form.email.trim()) {
      nextErrors.email = "Please enter your email address.";
    } else if (!/^\S+@\S+\.\S+$/.test(form.email)) {
      nextErrors.email = "Please enter a valid email address.";
    }

    if (!form.password) {
      nextErrors.password = "Please create a password.";
    } else if (form.password.length < 8) {
      nextErrors.password = "Password must be at least 8 characters.";
    }

    if (form.confirmPassword !== form.password) {
      nextErrors.confirmPassword = "Passwords do not match.";
    }

    if (!form.teamName.trim()) {
      nextErrors.teamName = "Please add your team or class name.";
    }

    if (!form.agreeToTerms) {
      nextErrors.agreeToTerms = "You must accept the terms to continue.";
    }

    return nextErrors;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const nextErrors = validateForm();
    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);

    await new Promise((resolve) => {
      setTimeout(resolve, 800);
    });

    setRegisteredUser({
      fullName: form.fullName,
      email: form.email,
      role: form.role,
      experience: form.experience,
      learningFocus: form.learningFocus,
      teamName: form.teamName
    });

    setIsSubmitting(false);
  };

  const handleReset = () => {
    setForm(initialForm);
    setErrors({});
    setRegisteredUser(null);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "32px 20px",
        fontFamily: '"Segoe UI", "Helvetica Neue", sans-serif',
        background:
          "radial-gradient(circle at top left, #f7c98b 0%, rgba(247, 201, 139, 0) 28%), radial-gradient(circle at top right, #b7dfc8 0%, rgba(183, 223, 200, 0) 34%), linear-gradient(135deg, #f7f2e9 0%, #e7efe7 45%, #d9e5dd 100%)",
        color: "#203127"
      }}
    >
      <div
        style={{
          maxWidth: "1160px",
          margin: "0 auto",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
          gap: "24px",
          alignItems: "stretch"
        }}
      >
        <section
          style={{
            ...cardStyle,
            padding: "36px",
            position: "relative",
            overflow: "hidden"
          }}
        >
          <div
            style={{
              position: "absolute",
              top: "-60px",
              right: "-40px",
              width: "180px",
              height: "180px",
              borderRadius: "999px",
              background: "rgba(244, 156, 76, 0.18)"
            }}
          />

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
              margin: "24px 0 14px",
              fontSize: "clamp(2.2rem, 4vw, 4rem)",
              lineHeight: 1,
              letterSpacing: "-0.04em"
            }}
          >
            Build your learning profile before the sprint starts.
          </h1>

          <p
            style={{
              margin: 0,
              maxWidth: "520px",
              fontSize: "17px",
              lineHeight: 1.6,
              color: "rgba(32, 49, 39, 0.78)"
            }}
          >
            Register once, map your current role, and let the coach tailor
            future goals, assessments, and practice recommendations to your
            team context.
          </p>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
              gap: "14px",
              marginTop: "28px"
            }}
          >
            {[
              ["Personalized roadmap", "Track the skills you want to grow next."],
              ["Team-aware setup", "Organize members by role, squad, or class."],
              ["Ready for backend", "Swap the mock submit with your API later."]
            ].map(([title, body]) => (
              <div
                key={title}
                style={{
                  padding: "18px",
                  borderRadius: "20px",
                  background: "rgba(255, 255, 255, 0.62)",
                  border: "1px solid rgba(24, 37, 28, 0.08)"
                }}
              >
                <strong style={{ display: "block", marginBottom: "8px" }}>
                  {title}
                </strong>
                <span style={{ color: "rgba(32, 49, 39, 0.72)" }}>{body}</span>
              </div>
            ))}
          </div>
        </section>

        <section style={{ ...cardStyle, padding: "32px" }}>
          <div style={{ marginBottom: "24px" }}>
            <h2 style={{ margin: "0 0 8px", fontSize: "28px" }}>
              Registration
            </h2>
            <p style={{ margin: 0, color: "rgba(32, 49, 39, 0.72)" }}>
              Create your account to start building your Scrum AI Coach profile.
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                gap: "16px"
              }}
            >
              <label>
                <span style={{ display: "block", marginBottom: "8px", fontWeight: 600 }}>
                  Full name
                </span>
                <input
                  type="text"
                  value={form.fullName}
                  onChange={(event) => updateField("fullName", event.target.value)}
                  placeholder="Nguyen Van A"
                  style={fieldStyle}
                />
                {errors.fullName && (
                  <span style={{ display: "block", marginTop: "6px", color: "#b3481f" }}>
                    {errors.fullName}
                  </span>
                )}
              </label>

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
                  placeholder="At least 8 characters"
                  style={fieldStyle}
                />
                {errors.password && (
                  <span style={{ display: "block", marginTop: "6px", color: "#b3481f" }}>
                    {errors.password}
                  </span>
                )}
              </label>

              <label>
                <span style={{ display: "block", marginBottom: "8px", fontWeight: 600 }}>
                  Confirm password
                </span>
                <input
                  type="password"
                  value={form.confirmPassword}
                  onChange={(event) => updateField("confirmPassword", event.target.value)}
                  placeholder="Repeat your password"
                  style={fieldStyle}
                />
                {errors.confirmPassword && (
                  <span style={{ display: "block", marginTop: "6px", color: "#b3481f" }}>
                    {errors.confirmPassword}
                  </span>
                )}
              </label>

              <label>
                <span style={{ display: "block", marginBottom: "8px", fontWeight: 600 }}>
                  Role
                </span>
                <select
                  value={form.role}
                  onChange={(event) => updateField("role", event.target.value)}
                  style={fieldStyle}
                >
                  <option>Developer</option>
                  <option>Scrum Master</option>
                  <option>Product Owner</option>
                  <option>Student</option>
                </select>
              </label>

              <label>
                <span style={{ display: "block", marginBottom: "8px", fontWeight: 600 }}>
                  Experience level
                </span>
                <select
                  value={form.experience}
                  onChange={(event) => updateField("experience", event.target.value)}
                  style={fieldStyle}
                >
                  <option>0-1 years</option>
                  <option>1-3 years</option>
                  <option>3-5 years</option>
                  <option>5+ years</option>
                </select>
              </label>

              <label>
                <span style={{ display: "block", marginBottom: "8px", fontWeight: 600 }}>
                  Learning focus
                </span>
                <select
                  value={form.learningFocus}
                  onChange={(event) => updateField("learningFocus", event.target.value)}
                  style={fieldStyle}
                >
                  <option>Agile foundations</option>
                  <option>Technical growth</option>
                  <option>Leadership skills</option>
                  <option>Delivery excellence</option>
                </select>
              </label>

              <label>
                <span style={{ display: "block", marginBottom: "8px", fontWeight: 600 }}>
                  Team or class
                </span>
                <input
                  type="text"
                  value={form.teamName}
                  onChange={(event) => updateField("teamName", event.target.value)}
                  placeholder="Scrum Team Alpha"
                  style={fieldStyle}
                />
                {errors.teamName && (
                  <span style={{ display: "block", marginTop: "6px", color: "#b3481f" }}>
                    {errors.teamName}
                  </span>
                )}
              </label>
            </div>

            <label
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: "12px",
                marginTop: "20px",
                color: "rgba(32, 49, 39, 0.82)"
              }}
            >
              <input
                type="checkbox"
                checked={form.agreeToTerms}
                onChange={(event) => updateField("agreeToTerms", event.target.checked)}
                style={{ marginTop: "4px" }}
              />
              <span>
                I agree to create a learning profile and store my registration
                details for future coaching features.
              </span>
            </label>

            {errors.agreeToTerms && (
              <div style={{ marginTop: "8px", color: "#b3481f" }}>
                {errors.agreeToTerms}
              </div>
            )}

            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "12px",
                marginTop: "24px"
              }}
            >
              <button
                type="submit"
                disabled={isSubmitting}
                style={{
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
                {isSubmitting ? "Creating account..." : "Create account"}
              </button>

              <button
                type="button"
                onClick={handleReset}
                style={{
                  padding: "14px 22px",
                  borderRadius: "16px",
                  border: "1px solid rgba(29, 43, 35, 0.16)",
                  background: "transparent",
                  color: "#203127",
                  fontSize: "15px",
                  fontWeight: 700,
                  cursor: "pointer"
                }}
              >
                Reset
              </button>
            </div>
          </form>

          {registeredUser && (
            <div
              style={{
                marginTop: "24px",
                padding: "20px",
                borderRadius: "22px",
                background: "linear-gradient(135deg, #203127 0%, #2f4a3b 100%)",
                color: "#f9f4ea"
              }}
            >
              <div
                style={{
                  fontSize: "13px",
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  opacity: 0.72
                }}
              >
                Registration preview
              </div>
              <h3 style={{ margin: "10px 0 8px", fontSize: "24px" }}>
                Welcome, {registeredUser.fullName}
              </h3>
              <p style={{ margin: 0, lineHeight: 1.7 }}>
                {registeredUser.role} from {registeredUser.teamName} registered
                with {registeredUser.experience} experience and a focus on{" "}
                {registeredUser.learningFocus}.
              </p>
              <p style={{ margin: "12px 0 0", opacity: 0.8 }}>
                Email: {registeredUser.email}
              </p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;

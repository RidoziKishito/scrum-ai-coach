import { useState } from "react";

function App() {

  // Course được chọn
  const [course, setCourse] = useState("Kỹ thuật lập trình");

  // Điểm rating
  const [technical, setTechnical] = useState(1);
  const [softSkills, setSoftSkills] = useState(1);
  const [domainKnowledge, setDomainKnowledge] = useState(1);

  // Summary
  const [summary, setSummary] = useState(null);

  // Submit
  const handleSubmit = async () => {

    const data = {
      user_id: "user_001",
      course_name: course,
      ratings: [
        {
          skill_type: "Technical",
          rating: technical
        },
        {
          skill_type: "Soft Skills",
          rating: softSkills
        },
        {
          skill_type: "Domain Knowledge",
          rating: domainKnowledge
        }
      ]
    };

    console.log(data);

    // Gửi sang backend
    const response = await fetch("http://127.0.0.1:8000/skill-assessment", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    console.log(result);

    setSummary(result.summary);
  };

  return (
    <div style={{ padding: "30px" }}>

      <h1>Assess Current Skills</h1>

      {/* CHỌN COURSE */}
      <h3>Choose Course</h3>

      <select
        value={course}
        onChange={(e) => setCourse(e.target.value)}
      >
        <option>Kỹ thuật lập trình</option>
        <option>OOP</option>
        <option>Database System</option>
      </select>

      <hr />

      {/* TECHNICAL */}
      <h3>Technical: {technical}</h3>

      <input
        type="range"
        min="1"
        max="5"
        value={technical}
        onChange={(e) => setTechnical(Number(e.target.value))}
      />

      {/* SOFT SKILLS */}
      <h3>Soft Skills: {softSkills}</h3>

      <input
        type="range"
        min="1"
        max="5"
        value={softSkills}
        onChange={(e) => setSoftSkills(Number(e.target.value))}
      />

      {/* DOMAIN KNOWLEDGE */}
      <h3>Domain Knowledge: {domainKnowledge}</h3>

      <input
        type="range"
        min="1"
        max="5"
        value={domainKnowledge}
        onChange={(e) => setDomainKnowledge(Number(e.target.value))}
      />

      <br />
      <br />

      <button onClick={handleSubmit}>
        Submit Assessment
      </button>

      {/* SUMMARY */}
      {summary && (
        <div style={{
          marginTop: "30px",
          border: "1px solid gray",
          padding: "20px"
        }}>

          <h2>Skill Profile Summary</h2>

          <p>Course: {summary.course_name}</p>

          <p>Average Score: {summary.average_score}</p>

          <p>Level: {summary.level}</p>

        </div>
      )}

    </div>
  );
}

export default App;
// src/services/assessmentApi.js

const MOCK_COURSES = [
  { id: 'c_01', name: 'Programming Fundamentals', image: '/images/programming.png' },
  { id: 'c_02', name: 'Python', image: '/images/python.png' },
  { id: 'c_03', name: 'Web Development (Frontend)', image: '/images/web.png' },
  { id: 'c_04', name: 'Backend Development', image: '/images/backend.png' },
  { id: 'c_05', name: 'Database & SQL', image: '/images/sql-server.png' },
  { id: 'c_06', name: 'Version Control (Git)', image: '/images/git.png' },
  { id: 'c_07', name: 'Testing & QA', image: '/images/testing.png' },
  { id: 'c_08', name: 'System Design & Architecture', image: '/images/system-design.png' },
  { id: 'c_09', name: 'DevOps & Deployment', image: '/images/devops.png' },
  { id: 'c_10', name: 'AI & Machine Learning Basics', image: '/images/ai.png' }
];

const assessmentApi = {
  getSkills: async () => {
    return new Promise((resolve) => {
      setTimeout(() => resolve({ data: MOCK_COURSES }), 300);
    });
  },
  
  submitAssessment: async (payload) => {
    return new Promise((resolve) => {
      // LOG PAYLOAD RÕ RÀNG ĐỂ KIỂM TRA
      console.log("🚀 Payload to Backend:", JSON.stringify(payload, null, 2));
      setTimeout(() => resolve({ data: { message: "Success" } }), 1500);
    });
  }
};

export default assessmentApi;
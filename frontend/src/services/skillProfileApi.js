import supabase from './supabaseClient';
import { API_BASE_URL } from './apiConfig';

export const getSkillProfile = async () => {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;

  if (!token) {
    throw new Error("No access token found. Please log in again.");
  }

  localStorage.setItem("access_token", token);

  const response = await fetch(`${API_BASE_URL}/skills/profile`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`
    }
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Failed to fetch skill profile");
  }

  return await response.json();
};

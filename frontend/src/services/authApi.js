import { API_BASE_URL } from './apiConfig';

const REGISTER_ENDPOINT = `${API_BASE_URL}/auth/register`;

const authApi = {
    register: async (payload) => {
        const response = await fetch(REGISTER_ENDPOINT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(
                result?.message ||
                result?.detail ||
                "Registration failed. Please try again."
            );
        }

        return result;
    }
,

    updateRole: async (role) => {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/users/role`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ role })
        });

        const result = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(result?.message || 'Failed to update role');
        }

        return result;
    }
,

    updateProfile: async ({ display_name, role }) => {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/users/profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ display_name, role })
        });

        const result = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(result?.message || result?.detail || 'Failed to update profile');
        }

        return result;
    }
,

    getCurrentUser: async () => {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const result = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(result?.message || 'Failed to fetch current user');
        }

        return result;
    }
,

    syncAccount: async (accessToken) => {
        const response = await fetch(`${API_BASE_URL}/auth/sync-account`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            }
        });

        const result = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(result?.message || 'Failed to sync account');
        }

        return result;
    }
};

export default authApi;

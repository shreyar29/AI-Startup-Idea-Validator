export const setAuthData = (data) => {
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('username', data.username);
  localStorage.setItem('user_id', data.user_id);
  window.dispatchEvent(new Event('auth-change'));
};

export const clearAuthData = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  localStorage.removeItem('user_id');
  window.dispatchEvent(new Event('auth-change'));
};

export const getAuthToken = () => {
  return localStorage.getItem('token');
};

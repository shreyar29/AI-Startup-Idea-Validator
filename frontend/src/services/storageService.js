export const storageService = {
  setActiveReportId: (id) => {
    if (id) localStorage.setItem('active_report_id', id);
  },
  getActiveReportId: () => {
    return localStorage.getItem('active_report_id');
  },
  getUserId: () => {
    return localStorage.getItem('user_id');
  },
  getToken: () => {
    return localStorage.getItem('token');
  },
  clearActiveSession: () => {
    localStorage.removeItem('active_report_id');
  }
};

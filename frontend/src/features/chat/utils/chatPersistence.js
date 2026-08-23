export const loadChatHistory = (sessionId) => {
  if (!sessionId) return null;
  try {
    const data = localStorage.getItem(`chat_${sessionId}`);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('Failed to load chat history', error);
    return null;
  }
};

export const saveChatHistory = (sessionId, messages) => {
  if (!sessionId) return;
  try {
    localStorage.setItem(`chat_${sessionId}`, JSON.stringify(messages));
  } catch (error) {
    console.error('Failed to save chat history', error);
  }
};

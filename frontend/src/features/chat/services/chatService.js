import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');

export const chatService = {
  // We keep sendMessage for backwards compatibility if any legacy component uses it.
  async sendMessage(sessionId, query, activeSection) {
    throw new Error('sendMessage is deprecated. Use streamMessage instead.');
  },
  
  async streamMessage(sessionId, query, activeSection, veraMode, onChunk, onComplete, onError) {
    try {
      // Get the token if we use authentication
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          session_id: sessionId,
          question: query,
          active_section: activeSection || 'overview',
          vera_mode: veraMode || 'Founder'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let done = false;
      let fullResponse = '';

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunkString = decoder.decode(value, { stream: true });
          const lines = chunkString.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.replace('data: ', '').trim();
              if (dataStr === '[DONE]') {
                done = true;
                break;
              }
              if (dataStr.startsWith('{')) {
                try {
                  const dataObj = JSON.parse(dataStr);
                  if (dataObj.error) {
                    onError(new Error(dataObj.error));
                    return;
                  }
                  if (dataObj.chunk) {
                    fullResponse += dataObj.chunk;
                    onChunk(dataObj.chunk);
                  }
                } catch (e) {
                  console.error("Error parsing SSE chunk", e);
                }
              }
            }
          }
        }
      }
      
      if (onComplete) {
        onComplete(fullResponse);
      }
      
    } catch (error) {
      if (onError) {
        onError(error);
      }
    }
  },

  async clearSession(sessionId) {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_URL}/api/chat/session/${sessionId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to clear session: ${response.status}`);
    }
    return response.json();
  }
};

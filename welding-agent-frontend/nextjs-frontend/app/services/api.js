// Service for communicating with the Flask backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api';

export const apiService = {
  // Health check endpoint
  async health() {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    
    return response.json();
  },

  // Ask a question endpoint
  async askQuestion(question) {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Request failed: ${response.status}`);
    }
    
    return response.json();
  },

  // Get stats endpoint
  async getStats() {
    const response = await fetch(`${API_BASE_URL}/stats`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get stats: ${response.status}`);
    }
    
    return response.json();
  },

  // Analyze image endpoint
  async analyzeImage(imagePath, noteTitle) {
    const response = await fetch(`${API_BASE_URL}/analyze-image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image_path: imagePath, note_title: noteTitle }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Request failed: ${response.status}`);
    }
    
    return response.json();
  },

  // Upload PDF endpoint
  async uploadPdf(pdfPath) {
    const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pdf_path: pdfPath }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Request failed: ${response.status}`);
    }
    
    return response.json();
  },

  // Start autonomous mode
  async startAutonomousMode(options = {}) {
    const response = await fetch(`${API_BASE_URL}/autonomous/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(options),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Request failed: ${response.status}`);
    }
    
    return response.json();
  },

  // Stop autonomous mode
  async stopAutonomousMode() {
    const response = await fetch(`${API_BASE_URL}/autonomous/stop`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Request failed: ${response.status}`);
    }
    
    return response.json();
  }
};
'use client';

import { useState, useEffect } from 'react';
import styles from './page.module.css';

import Header from './components/Header';
import ChatContainer from './components/ChatContainer';
import InputArea from './components/InputArea';
import ConnectionStatus from './components/ConnectionStatus';

import { apiService } from './services/api';

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [stats, setStats] = useState({
    notes: 0,
    tags: 0,
  });

  // Parse <artifact> blocks from AI responses
  const parseArtifacts = (text) => {
    const artifactRegex =
      /<artifact\s+type="(.*?)">([\s\S]*?)<\/artifact>/g;

    const artifacts = [];

    const cleanText = text.replace(
      artifactRegex,
      (_, type, content) => {
        artifacts.push({
          type: type.trim(),
          content: content.trim(),
        });

        return '';
      }
    );

    return {
      text: cleanText.trim(),
      artifacts,
    };
  };

  // Initial connection + stats
  useEffect(() => {
    const initialize = async () => {
      try {
        const healthResponse =
          await apiService.health();

        setIsConnected(true);
        setStats(healthResponse);

        const statsResponse =
          await apiService.getStats();

        setStats(statsResponse);
      } catch (error) {
        console.error(
          'Failed to connect to backend:',
          error
        );

        setIsConnected(false);
      }
    };

    initialize();

    // Poll connection status
    const interval = setInterval(() => {
      apiService
        .health()
        .then(() => {
          if (!isConnected) {
            setIsConnected(true);

            apiService
              .getStats()
              .then(setStats);
          }
        })
        .catch(() => {
          if (isConnected) {
            setIsConnected(false);
          }
        });
    }, 5000);

    return () => clearInterval(interval);
  }, [isConnected]);

  // Submit message
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!input.trim() || loading) return;

    const question = input.trim();

    setInput('');
    setLoading(true);

    // Add user message
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        text: question,
        isUser: true,
        sources: [],
        contextUsed: false,
        timestamp: new Date(),
        artifacts: [],
      },
    ]);

    try {
      const response =
        await apiService.askQuestion(question);

      // Parse artifacts from AI response
      const parsed = parseArtifacts(
        response.answer || ''
      );

      // Add bot message
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: parsed.text,
          artifacts: parsed.artifacts,
          isUser: false,
          sources: response.sources || [],
          contextUsed:
            response.context_used || false,
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      console.error(
        'Error asking question:',
        error
      );

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: `I encountered an error: ${error.message}`,
          isUser: false,
          sources: [],
          contextUsed: false,
          timestamp: new Date(),
          artifacts: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const handlePrompt = (question) => {
    setInput(question);

    setTimeout(() => {
      const textarea =
        document.querySelector('textarea');

      if (textarea) textarea.focus();
    }, 100);
  };

  return (
    <div className={styles.page}>
      <Header
        isConnected={isConnected}
        stats={stats}
      />

      <ConnectionStatus
        isConnected={isConnected}
      />

      <main className={styles.main}>
        <div className={styles.chatContainer}>
          <ChatContainer
            messages={messages}
            loading={loading}
          />

          {!messages.length && !loading && (
            <div
              className={styles.welcomeScreen}
            >
              <div
                className={styles.welcomeIcon}
              >
                🤖
              </div>

              <h2>
                Welcome to Prox Welding
                Assistant
              </h2>

              <p>
                Ask questions about welding
                procedures, safety, and
                equipment
              </p>

              <div
                className={styles.quickPrompts}
              >
                <button
                  onClick={() =>
                    handlePrompt(
                      "What's the duty cycle for MIG welding at 200A?"
                    )
                  }
                  className={
                    styles.promptButton
                  }
                >
                  What's the duty cycle for
                  MIG welding at 200A?
                </button>

                <button
                  onClick={() =>
                    handlePrompt(
                      'How do I set up TIG welding?'
                    )
                  }
                  className={
                    styles.promptButton
                  }
                >
                  How do I set up TIG
                  welding?
                </button>

                <button
                  onClick={() =>
                    handlePrompt(
                      'What are the safety precautions?'
                    )
                  }
                  className={
                    styles.promptButton
                  }
                >
                  What are the safety
                  precautions?
                </button>

                <button
                  onClick={() =>
                    handlePrompt(
                      'What equipment do I need?'
                    )
                  }
                  className={
                    styles.promptButton
                  }
                >
                  What equipment do I need?
                </button>
              </div>
            </div>
          )}
        </div>

        <InputArea
          input={input}
          setInput={setInput}
          loading={loading}
          onSubmit={handleSubmit}
          onClearChat={handleClearChat}
          disabled={false}
        />
      </main>
    </div>
  );
}
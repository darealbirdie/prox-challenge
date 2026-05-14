'use client';

import styles from './Message.module.css';
import ReactMarkdown from 'react-markdown';
import MermaidDiagram from './MermaidDiagram';

export default function Message({
  id,
  text,
  isUser,
  sources = [],
  contextUsed = false,
  timestamp,
  artifacts = [],
}) {
  // Format timestamp as HH:MM AM/PM
  let formattedTime = '';

  if (timestamp) {
    const date = timestamp instanceof Date
      ? timestamp
      : new Date(timestamp);

    const hours = date.getHours();
    const minutes = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const hours12 = hours % 12 || 12;

    formattedTime = `${hours12}:${minutes
      .toString()
      .padStart(2, '0')} ${ampm}`;
  }

  return (
    <div
      id={`message-${id}`}
      className={`${styles.message} ${
        isUser ? styles.userMessage : styles.botMessage
      }`}
    >
      {!isUser && (
        <div className={styles.botAvatar}>
          🤖
        </div>
      )}

      <div className={styles.messageContent}>
        <div className={styles.messageHeader}>
          <span className={styles.messageAuthor}>
            {isUser ? 'You:' : 'Bot:'}
          </span>

          <span className={styles.messageTime}>
            {formattedTime}
          </span>
        </div>

        <div className={styles.messageText}>
          <ReactMarkdown>
            {text}
          </ReactMarkdown>
        </div>

        {artifacts.length > 0 && (
          <div className={styles.artifactsContainer}>
            {artifacts.map((artifact, index) => (
              <div
                key={index}
                className={styles.artifactItem}
              >
                <div className={styles.artifactHeader}>
                  <span className={styles.artifactType}>
                    {artifact.type.toUpperCase()}
                  </span>
                </div>

                <div className={styles.artifactContent}>
                  {artifact.type.toLowerCase() === 'mermaid' ? (
                    <MermaidDiagram
                      chart={artifact.content}
                    />
                  ) : (
                    <pre className={styles.artifactCode}>
                      <code>{artifact.content}</code>
                    </pre>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {sources.length > 0 && (
          <div className={styles.sources}>
            <span className={styles.sourcesLabel}>
              📚 Sources:
            </span>

            {sources.map((source, index) => (
              <span
                key={index}
                className={styles.sourceTag}
              >
                {source}
              </span>
            ))}
          </div>
        )}

        {contextUsed && (
          <div className={styles.contextBadge}>
            Used context from knowledge base
          </div>
        )}
      </div>

      {isUser && (
        <div className={styles.userAvatar}>
          👤
        </div>
      )}
    </div>
  );
}
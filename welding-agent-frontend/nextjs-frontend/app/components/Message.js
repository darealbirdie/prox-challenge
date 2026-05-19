'use client';

import styles from './Message.module.css';

import ReactMarkdown from 'react-markdown';
import MermaidDiagram from './MermaidDiagram';

function ArtifactRenderer({ artifact }) {
  const type = artifact.type.toLowerCase();

  // MERMAID
  if (type === 'mermaid') {
    return (
      <MermaidDiagram
        chart={artifact.content}
      />
    );
  }

  // HTML PREVIEW
  if (type === 'html') {
    return (
      <iframe
        srcDoc={artifact.content}
        title="HTML Artifact"
        style={{
          width: '100%',
          minHeight: '400px',
          border: 'none',
          borderRadius: '8px',
          background: 'white',
        }}
      />
    );
  }

  // MARKDOWN
  if (type === 'markdown') {
    return (
      <div className={styles.markdownArtifact}>
        <ReactMarkdown>
          {artifact.content}
        </ReactMarkdown>
      </div>
    );
  }

  // JSON
  if (type === 'json') {
    try {
      const formatted = JSON.stringify(
        JSON.parse(artifact.content),
        null,
        2
      );

      return (
        <pre className={styles.artifactCode}>
          <code>{formatted}</code>
        </pre>
      );
    } catch {
      return (
        <pre className={styles.artifactCode}>
          <code>{artifact.content}</code>
        </pre>
      );
    }
  }

  // IMAGE
  if (type === 'image') {
    return (
      <img
        src={artifact.content}
        alt="Artifact"
        style={{
          maxWidth: '100%',
          borderRadius: '8px',
        }}
      />
    );
  }

  // SVG
  if (type === 'svg') {
    return (
      <div
        dangerouslySetInnerHTML={{
          __html: artifact.content,
        }}
      />
    );
  }

  // DEFAULT CODE BLOCK
  return (
    <pre className={styles.artifactCode}>
      <code>{artifact.content}</code>
    </pre>
  );
}

export default function Message({
  id,
  text,
  isUser,
  sources = [],
  contextUsed = false,
  timestamp,
  artifacts = [],
}) {
  // Format timestamp
  let formattedTime = '';

  if (timestamp) {
    const date =
      timestamp instanceof Date
        ? timestamp
        : new Date(timestamp);

    const hours = date.getHours();
    const minutes = date.getMinutes();

    const ampm =
      hours >= 12 ? 'PM' : 'AM';

    const hours12 = hours % 12 || 12;

    formattedTime = `${hours12}:${minutes
      .toString()
      .padStart(2, '0')} ${ampm}`;
  }

  return (
    <div
      id={`message-${id}`}
      className={`${styles.message} ${
        isUser
          ? styles.userMessage
          : styles.botMessage
      }`}
    >
      {!isUser && (
        <div className={styles.botAvatar}>
          🤖
        </div>
      )}

      <div className={styles.messageContent}>
        {/* HEADER */}
        <div className={styles.messageHeader}>
          <span className={styles.messageAuthor}>
            {isUser ? 'You:' : 'Bot:'}
          </span>

          <span className={styles.messageTime}>
            {formattedTime}
          </span>
        </div>

        {/* MESSAGE TEXT */}
        <div className={styles.messageText}>
          <ReactMarkdown>
            {text}
          </ReactMarkdown>
        </div>

        {/* ARTIFACTS */}
        {artifacts.length > 0 && (
          <div
            className={
              styles.artifactsContainer
            }
          >
            {artifacts.map(
              (artifact, index) => (
                <div
                  key={index}
                  className={
                    styles.artifactItem
                  }
                >
                  <div
                    className={
                      styles.artifactHeader
                    }
                  >
                    <span
                      className={
                        styles.artifactType
                      }
                    >
                      {artifact.type.toUpperCase()}
                    </span>
                  </div>

                  <div
                    className={
                      styles.artifactContent
                    }
                  >
                    <ArtifactRenderer
                      artifact={artifact}
                    />
                  </div>
                </div>
              )
            )}
          </div>
        )}

        {/* SOURCES */}
        {sources.length > 0 && (
          <div className={styles.sources}>
            <span
              className={
                styles.sourcesLabel
              }
            >
              📚 Sources:
            </span>

            {sources.map(
              (source, index) => (
                <span
                  key={index}
                  className={
                    styles.sourceTag
                  }
                >
                  {source}
                </span>
              )
            )}
          </div>
        )}

        {/* CONTEXT BADGE */}
        {contextUsed && (
          <div
            className={styles.contextBadge}
          >
            Used context from knowledge
            base
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
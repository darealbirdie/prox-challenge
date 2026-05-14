'use client';

import styles from './ChatContainer.module.css';
import Message from './Message';

export default function ChatContainer({ messages, loading }) {
  return (
    <div className={styles.chatContainer}>
      {messages.map((message) => (
        <Message
          key={message.id}
          id={message.id}
          artifacts={message.artifacts || []}
          text={message.text}
          isUser={message.isUser}
          sources={message.sources}
          contextUsed={message.contextUsed}
          timestamp={message.timestamp}
        />
      ))}
      
      {loading && (
        <div className={styles.loadingIndicator}>
          <div className={styles.thinkingIcon}>🤖</div>
          <div className={styles.thinkingText}>Thinking...</div>
          <div className={styles.typingDots}>
            <div className={styles.dot}></div>
            <div className={styles.dot}></div>
            <div className={styles.dot}></div>
          </div>
        </div>
      )}
    </div>
  );
}
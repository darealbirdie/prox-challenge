'use client';

import { useState, useEffect } from 'react';
import styles from './InputArea.module.css';

export default function InputArea({ input, setInput, loading, onSubmit, onClearChat, disabled }) {
  const [showClear, setShowClear] = useState(false);

  // Update showClear based on input value
  useEffect(() => {
    if (input.trim() !== '') {
      setShowClear(true);
    } else {
      setShowClear(false);
    }
  }, [input]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e);
    }
  };

  return (
    <div className={styles.inputArea}>
      <div className={styles.inputContainer}>
         <textarea
           value={input}
           onChange={(e) => setInput(e.target.value)}
           onKeyPress={handleKeyPress}
           placeholder="Ask about welding procedures, safety, equipment..."
           rows={3}
           disabled={disabled || loading}
           className={styles.textarea}
         />
        <div className={styles.inputButtons}>
          {!loading && !disabled && (
            <button
              onClick={onClearChat}
              disabled={!showClear}
              className={`${styles.button} ${styles.clearButton}`}
            >
              Clear
            </button>
          )}
          <button
            type="submit"
            onClick={onSubmit}
            disabled={disabled || loading || !input.trim()}
            className={`${styles.button} ${styles.sendButton}`}
          >
            {loading ? 'Thinking...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}
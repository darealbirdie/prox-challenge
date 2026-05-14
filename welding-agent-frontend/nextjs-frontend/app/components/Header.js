'use client';

import styles from './Header.module.css';

export default function Header({ isConnected, stats }) {
  return (
    <header className={styles.header}>
      <div className={styles.headerContent}>
        <div className={styles.headerLeft}>
          <span className={styles.agentIcon}>🤖</span>
          <span className={styles.agentName}>Prox Welding Agent</span>
        </div>
        <div className={styles.headerCenter}>
          <span className={styles.connectionStatus}>
            {isConnected ? '🔵 Connected' : '🔴 Disconnected'}
          </span>
        </div>
        <div className={styles.headerRight}>
          <span className={styles.stats}>
            📚 {stats.notes} notes • 🏷️ {stats.tags} tags
          </span>
        </div>
      </div>
    </header>
  );
}
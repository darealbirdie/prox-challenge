'use client';

import styles from './ConnectionStatus.module.css';

export default function ConnectionStatus({ isConnected }) {
  return (
    <div className={styles.connectionStatus}>
      {isConnected ? (
        <span className={styles.statusConnected}>
          🟢 Connected
        </span>
      ) : (
        <span className={styles.statusDisconnected}>
          🔴 Disconnected
        </span>
      )}
    </div>
  );
}
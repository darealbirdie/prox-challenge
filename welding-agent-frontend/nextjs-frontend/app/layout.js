export const metadata = {
  title: "Prox Welding Agent",
  description: "Welding Assistant powered by Claude AI",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
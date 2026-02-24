import './globals.css'
import 'leaflet/dist/leaflet.css'

export const metadata = {
  title: 'Velora - Employee Transportation Optimization',
  description: 'Optimize corporate employee transportation with AI-powered routing',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gray-50">{children}</body>
    </html>
  )
}

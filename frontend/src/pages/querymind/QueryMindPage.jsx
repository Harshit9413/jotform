import { useState } from 'react'
import ConnectScreen from './ConnectScreen'
import ChatScreen from './ChatScreen'

export default function QueryMindPage() {
  const [session, setSession] = useState(null)

  return session
    ? <ChatScreen session={session} onDisconnect={() => setSession(null)} />
    : <ConnectScreen onConnect={setSession} />
}

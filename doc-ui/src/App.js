import { useState, useRef, useEffect } from "react";
import axios from "axios";

const API = "http://localhost:3001";

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! I am your Documentation Assistant. Ask me anything about Python, FastAPI, PostgreSQL, or RabbitMQ.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    const question = input.trim();
    if (!question || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);

    try {
      const postRes = await axios.post(`${API}/questions`, {
        asked_by: "user@docassistant.com",
        subject: "Query",
        body: question,
      });

      const questionId = postRes.data.questionId;

      let answer = null;
      let attempts = 0;

      while (!answer && attempts < 30) {
        await new Promise((r) => setTimeout(r, 3000));
        const getRes = await axios.get(
          `${API}/questions/${questionId}/answer`
        );
        if (getRes.data.status === "completed") {
          answer = getRes.data;
        }
        attempts++;
      }

      if (answer) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: answer.answer,
            meta: {
              confidence: answer.confidence_score,
              classification: answer.classification,
            },
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: "Answer is taking longer than expected. Please try again.",
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Error connecting to server. Please check if services are running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div style={styles.app}>
      <div style={styles.header}>
        <h2 style={styles.headerTitle}>Doc Assistant</h2>
        <p style={styles.headerSub}>
          Ask questions about Python, FastAPI, PostgreSQL, RabbitMQ
        </p>
      </div>

      <div style={styles.messages}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.msgRow,
              justifyContent:
                msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <div
              style={{
                ...styles.bubble,
                backgroundColor:
                  msg.role === "user" ? "#0070f3" : "#1e1e1e",
              }}
            >
              <p style={styles.msgText}>{msg.text}</p>
              {msg.meta && (
                <div style={styles.meta}>
                  <span
                    style={{
                      ...styles.badge,
                      backgroundColor:
                        msg.meta.classification === "auto_answer"
                          ? "#16a34a"
                          : "#ca8a04",
                    }}
                  >
                    {msg.meta.classification}
                  </span>
                  <span style={styles.score}>
                    confidence: {msg.meta.confidence}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ ...styles.msgRow, justifyContent: "flex-start" }}>
            <div style={{ ...styles.bubble, backgroundColor: "#1e1e1e" }}>
              <p style={{ ...styles.msgText, color: "#888" }}>
                Searching documentation... ⏳
              </p>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div style={styles.inputArea}>
        <textarea
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask a question... (Enter to send)"
          rows={2}
          disabled={loading}
        />
        <button
          style={{
            ...styles.btn,
            backgroundColor: loading ? "#555" : "#0070f3",
            cursor: loading ? "not-allowed" : "pointer",
          }}
          onClick={sendMessage}
          disabled={loading}
        >
          {loading ? "⏳" : "Send"}
        </button>
      </div>
    </div>
  );
}

const styles = {
  app: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    backgroundColor: "#0a0a0a",
    fontFamily: "sans-serif",
  },
  header: {
    padding: "16px 24px",
    borderBottom: "1px solid #222",
    backgroundColor: "#111",
  },
  headerTitle: {
    color: "#fff",
    margin: 0,
    fontSize: "20px",
  },
  headerSub: {
    color: "#888",
    margin: "4px 0 0",
    fontSize: "13px",
  },
  messages: {
    flex: 1,
    overflowY: "auto",
    padding: "24px",
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  msgRow: {
    display: "flex",
  },
  bubble: {
    padding: "12px 16px",
    borderRadius: "12px",
    maxWidth: "70%",
  },
  msgText: {
    margin: 0,
    fontSize: "14px",
    lineHeight: "1.6",
    color: "#fff",
    whiteSpace: "pre-wrap",
  },
  meta: {
    marginTop: "8px",
    display: "flex",
    gap: "8px",
    alignItems: "center",
  },
  badge: {
    padding: "2px 8px",
    borderRadius: "9999px",
    fontSize: "11px",
    color: "#fff",
    fontWeight: "600",
  },
  score: {
    fontSize: "11px",
    color: "#aaa",
  },
  inputArea: {
    display: "flex",
    gap: "8px",
    padding: "16px 24px",
    borderTop: "1px solid #222",
    backgroundColor: "#111",
  },
  input: {
    flex: 1,
    padding: "10px 14px",
    borderRadius: "8px",
    border: "1px solid #333",
    backgroundColor: "#1a1a1a",
    color: "#fff",
    fontSize: "14px",
    resize: "none",
    outline: "none",
  },
  btn: {
    padding: "10px 20px",
    borderRadius: "8px",
    border: "none",
    color: "#fff",
    fontSize: "14px",
    fontWeight: "600",
  },
};
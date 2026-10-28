import { useEffect, useRef, useState } from "react";
import {
  askStream,
  fetchConversation,
  fetchConversations,
  fetchTenants,
  sendFeedback,
  type Citation,
  type ConvSummary,
} from "./api";

type Msg = {
  id: string;
  role: "user" | "assistant";
  text: string;
  citations?: Citation[];
  pending?: boolean;
  refused?: boolean;
  latency?: number;
  feedback?: "up" | "down";
};

export default function App() {
  const [apiKey, setApiKey] = useState(() => sessionStorage.getItem("kb_key") ?? "");
  const [showKey, setShowKey] = useState(() => !sessionStorage.getItem("kb_key"));
  const [tenants, setTenants] = useState<string[]>([]);
  const [tenant, setTenant] = useState("demo");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [convs, setConvs] = useState<ConvSummary[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [convId, setConvId] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  function refreshConvs(key = apiKey, t = tenant) {
    if (!key) {
      setConvs([]);
      return;
    }
    fetchConversations(t, key).then(setConvs);
  }

  useEffect(() => {
    fetchTenants().then((list) => {
      setTenants(list);
      if (list.length && !list.includes(tenant)) setTenant(list[0]);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    refreshConvs(apiKey, tenant);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tenant, apiKey]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 刷新后恢复当前会话
  useEffect(() => {
    const saved = sessionStorage.getItem("kb_conv");
    const key = sessionStorage.getItem("kb_key");
    if (!saved || !key) return;
    fetchConversation(saved, key).then((rows) => {
      if (!rows.length) return;
      setConvId(saved);
      setMessages(
        rows.map((r) => ({
          id: r.id,
          role: r.role,
          text: r.content,
          citations: r.citations,
          latency: r.latency_ms ?? undefined,
          refused: !!r.refused,
        })),
      );
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (convId) sessionStorage.setItem("kb_conv", convId);
    else sessionStorage.removeItem("kb_conv");
  }, [convId]);

  function saveKey() {
    sessionStorage.setItem("kb_key", apiKey.trim());
    setApiKey(apiKey.trim());
    setShowKey(false);
    setError("");
    refreshConvs(apiKey.trim(), tenant);
  }

  function clearKey() {
    sessionStorage.removeItem("kb_key");
    setApiKey("");
    setShowKey(true);
    setConvs([]);
    setError("");
  }

  function switchTenant(next: string) {
    setTenant(next);
    setMessages([]);
    setConvId(null);
    setError("");
    setNotice(`已切换到知识库：${next}`);
  }

  function newChat() {
    setMessages([]);
    setConvId(null);
    setError("");
    setNotice("已开始新对话");
  }

  async function openConv(id: string) {
    if (!apiKey) return;
    const rows = await fetchConversation(id, apiKey);
    if (!rows.length) {
      setError("读取会话失败");
      return;
    }
    setConvId(id);
    setNotice("");
    setError("");
    setMessages(
      rows.map((r) => ({
        id: r.id,
        role: r.role,
        text: r.content,
        citations: r.citations,
        latency: r.latency_ms ?? undefined,
        refused: !!r.refused,
      })),
    );
  }

  async function send() {
    const q = input.trim();
    if (!q || sending) return;
    if (!apiKey) {
      setError("请先填写访问密钥");
      return;
    }
    setError("");
    setNotice("");
    setInput("");
    const aid = "pending";
    setMessages((m) => [
      ...m,
      { id: crypto.randomUUID(), role: "user", text: q },
      { id: aid, role: "assistant", text: "", pending: true },
    ]);
    setSending(true);
    try {
      await askStream(
        { question: q, apiKey, tenant, conversationId: convId },
        {
          onMeta: (d) => setConvId(d.conversation_id),
          onCitations: (citations) =>
            setMessages((m) => m.map((x) => (x.id === aid ? { ...x, citations } : x))),
          onToken: (t) =>
            setMessages((m) => m.map((x) => (x.id === aid ? { ...x, text: x.text + t } : x))),
          onDone: (d) => {
            setMessages((m) =>
              m.map((x) =>
                x.id === aid
                  ? { ...x, id: d.request_id, pending: false, latency: d.latency_ms, refused: d.refused }
                  : x,
              ),
            );
            setConvId(d.conversation_id);
            refreshConvs();
          },
          onError: (msg) => {
            setError(msg);
            setMessages((m) => m.map((x) => (x.id === aid ? { ...x, pending: false } : x)));
          },
        },
      );
    } catch (e) {
      setError((e as Error).message);
      setMessages((m) => m.map((x) => (x.id === aid ? { ...x, pending: false } : x)));
    } finally {
      setSending(false);
    }
  }

  async function feedback(msg: Msg, rating: "up" | "down") {
    if (msg.id === "pending") return;
    let reason: string | undefined;
    if (rating === "down") {
      const v = window.prompt("哪里不对？（可选：答非所问 / 引用不对 / 信息过期）");
      reason = v ?? undefined;
    }
    try {
      await sendFeedback({ messageId: msg.id, rating, reason, apiKey, tenant });
      setMessages((m) => m.map((x) => (x.id === msg.id ? { ...x, feedback: rating } : x)));
    } catch {
      setError("反馈提交失败");
    }
  }

  return (
    <div className="app">
      <header>
        <div className="brand">设备知识库问答</div>
        <div className="controls">
          <select value={tenant} onChange={(e) => switchTenant(e.target.value)}>
            {(tenants.length ? tenants : [tenant]).map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <button className="ghost" onClick={() => setShowKey((v) => !v)}>
            {apiKey ? "密钥已设置" : "填密钥"}
          </button>
        </div>
      </header>

      {showKey && (
        <div className="keybar">
          <p>访问密钥（只保存在本标签页，可随时更换）</p>
          <div className="row">
            <input
              type="password"
              placeholder="AGENT_API_KEY"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && saveKey()}
            />
            <button onClick={saveKey}>保存</button>
            {apiKey && (
              <button className="ghost" onClick={clearKey}>
                清除
              </button>
            )}
          </div>
        </div>
      )}

      {error && <div className="banner">{error}</div>}

      <div className="shell">
        <aside className="sidebar">
          <div className="side-head">
            <button className="new" onClick={newChat}>
              + 新对话
            </button>
          </div>
          <div className="conv-list">
            {!apiKey && <div className="side-empty">填密钥后显示历史</div>}
            {apiKey && convs.length === 0 && <div className="side-empty">暂无历史对话</div>}
            {convs.map((c) => (
              <div
                key={c.id}
                className={"conv" + (c.id === convId ? " active" : "")}
                onClick={() => openConv(c.id)}
                title={c.title}
              >
                <div className="title">{c.title || "未命名对话"}</div>
                <div className="meta">
                  {c.messages} 条 · {c.created_at?.slice(5, 16)}
                </div>
              </div>
            ))}
          </div>
        </aside>

        <div className="chat">
          <main>
            {notice && <div className="notice">{notice}</div>}
            {messages.length === 0 && !notice && (
              <div className="empty">问一个设备问题，例如：X1 系列热床最高允许温度是多少？</div>
            )}
            {messages.map((m) =>
              m.role === "user" ? (
                <div key={m.id} className="msg user">
                  {m.text}
                </div>
              ) : (
                <div key={m.id} className="msg bot">
                  <div className="head">
                    <span>{m.refused ? "未找到依据" : "回答"}</span>
                    <span>{m.pending ? "生成中…" : m.latency ? `${m.latency} ms` : ""}</span>
                  </div>
                  <div className="body">
                    {m.text || (m.pending ? "…" : "（空）")}
                    {m.pending && <span className="caret" />}
                  </div>
                  {!!m.citations?.length && (
                    <div className="cites">
                      {m.citations.map((c, i) => (
                        <div className="cite" key={`${c.source}-${i}`}>
                          <b>
                            {i + 1}. {c.source.split("/").pop()}
                          </b>
                          <div className="snip">{c.snippet.slice(0, 140)}…</div>
                        </div>
                      ))}
                    </div>
                  )}
                  {!m.pending && (
                    <div className="fb">
                      <button
                        className={m.feedback === "up" ? "on" : ""}
                        onClick={() => feedback(m, "up")}
                        aria-label="有帮助"
                      >
                        👍
                      </button>
                      <button
                        className={m.feedback === "down" ? "on" : ""}
                        onClick={() => feedback(m, "down")}
                        aria-label="没帮助"
                      >
                        👎
                      </button>
                    </div>
                  )}
                </div>
              ),
            )}
            <div ref={bottomRef} />
          </main>

          <footer>
            <div className="inner">
              <input
                value={input}
                placeholder="输入问题，回车发送"
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    send();
                  }
                }}
              />
              <button onClick={send} disabled={sending}>
                {sending ? "生成中" : "发送"}
              </button>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}

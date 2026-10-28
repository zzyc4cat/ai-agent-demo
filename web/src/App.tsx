import { useEffect, useRef, useState } from "react";
import {
  apiLogin,
  apiLogout,
  apiMe,
  apiRegister,
  askStream,
  deleteConversation,
  fetchConversation,
  fetchConversations,
  hasToken,
  patchConversation,
  sendFeedback,
  type Citation,
  type ConvSummary,
  type User,
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

/** 数据库存的是 UTC，展示时转本地。 */
function fmtTime(raw?: string): string {
  if (!raw) return "";
  const d = new Date(raw.replace(" ", "T") + "Z");
  if (Number.isNaN(d.getTime())) return raw.slice(5, 16);
  return d.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [booting, setBooting] = useState(true);

  useEffect(() => {
    if (!hasToken()) {
      setBooting(false);
      return;
    }
    apiMe().then((u) => {
      setUser(u);
      setBooting(false);
    });
  }, []);

  if (booting) return <div className="boot">加载中…</div>;
  if (!user) return <Login onSuccess={setUser} />;
  return <ChatApp user={user} onLogout={() => setUser(null)} />;
}

function Login({ onSuccess }: { onSuccess: (u: User) => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit() {
    if (busy) return;
    setError("");
    if (mode === "register" && password !== confirm) {
      setError("两次密码不一致");
      return;
    }
    setBusy(true);
    try {
      const u =
        mode === "login"
          ? await apiLogin(username.trim(), password)
          : await apiRegister(username.trim(), password);
      onSuccess(u);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-wrap">
      <div className="login-card">
        <h1>设备知识库问答</h1>
        <div className="tabs">
          <button className={mode === "login" ? "on" : ""} onClick={() => setMode("login")}>
            登录
          </button>
          <button className={mode === "register" ? "on" : ""} onClick={() => setMode("register")}>
            注册
          </button>
        </div>
        <input
          placeholder="用户名"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
        />
        <input
          type="password"
          placeholder={mode === "register" ? "密码（至少 8 位）" : "密码"}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete={mode === "login" ? "current-password" : "new-password"}
        />
        {mode === "register" && (
          <input
            type="password"
            placeholder="确认密码"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            autoComplete="new-password"
          />
        )}
        {error && <div className="login-error">{error}</div>}
        <button className="login-submit" onClick={submit} disabled={busy}>
          {busy ? "请稍候…" : mode === "login" ? "登录" : "注册并登录"}
        </button>
        <p className="login-hint">
          {mode === "login" ? "没有账号？切换到注册" : "注册后默认加入公共知识库"}
        </p>
      </div>
    </div>
  );
}

function ChatApp({ user, onLogout }: { user: User; onLogout: () => void }) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [convs, setConvs] = useState<ConvSummary[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [convId, setConvId] = useState<string | null>(null);
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  function refreshConvs() {
    fetchConversations().then(setConvs);
  }

  useEffect(() => {
    refreshConvs();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 刷新后恢复当前会话
  useEffect(() => {
    const saved = sessionStorage.getItem("kb_conv");
    if (!saved) return;
    fetchConversation(saved).then((rows) => {
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
  }, []);

  useEffect(() => {
    if (convId) sessionStorage.setItem("kb_conv", convId);
    else sessionStorage.removeItem("kb_conv");
  }, [convId]);

  useEffect(() => {
    if (!openMenu) return;
    const close = () => setOpenMenu(null);
    document.addEventListener("click", close);
    return () => document.removeEventListener("click", close);
  }, [openMenu]);

  async function logout() {
    await apiLogout();
    onLogout();
  }

  function newChat() {
    setMessages([]);
    setConvId(null);
    setError("");
    setNotice("已开始新对话");
  }

  async function openConv(id: string) {
    const rows = await fetchConversation(id);
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

  async function renameConv(c: ConvSummary) {
    setOpenMenu(null);
    const v = window.prompt("重命名会话", c.title || "");
    if (v === null) return;
    const title = v.trim();
    if (!title) return;
    if (await patchConversation(c.id, { title })) refreshConvs();
    else setError("重命名失败");
  }

  async function togglePin(c: ConvSummary) {
    setOpenMenu(null);
    if (await patchConversation(c.id, { pinned: !c.pinned })) refreshConvs();
    else setError("操作失败");
  }

  async function removeConv(c: ConvSummary) {
    setOpenMenu(null);
    if (!window.confirm(`删除会话「${c.title}」？此操作不可恢复。`)) return;
    if (!(await deleteConversation(c.id))) {
      setError("删除失败");
      return;
    }
    if (convId === c.id) newChat();
    refreshConvs();
  }

  async function send() {
    const q = input.trim();
    if (!q || sending) return;
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
        { question: q, conversationId: convId },
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
      const msg = (e as Error).message;
      setError(msg);
      setMessages((m) => m.map((x) => (x.id === aid ? { ...x, pending: false } : x)));
      if (msg.includes("未登录")) {
        await apiLogout();
        onLogout();
      }
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
      await sendFeedback({ messageId: msg.id, rating, reason });
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
          <span className="who">
            {user.username}
            {user.role === "admin" && <span className="role">管理员</span>}
          </span>
          <button className="ghost" onClick={logout}>
            退出
          </button>
        </div>
      </header>

      {error && <div className="banner">{error}</div>}

      <div className="shell">
        <aside className="sidebar">
          <div className="side-head">
            <button className="new" onClick={newChat}>
              + 新对话
            </button>
          </div>
          <div className="conv-list">
            {convs.length === 0 && <div className="side-empty">暂无历史对话</div>}
            {convs.map((c) => (
              <div
                key={c.id}
                className={"conv" + (c.id === convId ? " active" : "")}
                onClick={() => openConv(c.id)}
                title={c.title}
              >
                <div className="title">
                  {!!c.pinned && <span className="badge">置顶</span>}
                  {c.title || "未命名对话"}
                </div>
                <div className="meta">
                  {c.messages} 条 · {fmtTime(c.created_at)}
                </div>
                <button
                  className="more"
                  aria-label="会话操作"
                  onClick={(e) => {
                    e.stopPropagation();
                    setOpenMenu(openMenu === c.id ? null : c.id);
                  }}
                >
                  ⋯
                </button>
                {openMenu === c.id && (
                  <div className="menu" onClick={(e) => e.stopPropagation()}>
                    <button onClick={() => renameConv(c)}>重命名</button>
                    <button onClick={() => togglePin(c)}>
                      {c.pinned ? "取消置顶" : "置顶"}
                    </button>
                    <button className="danger" onClick={() => removeConv(c)}>
                      删除
                    </button>
                  </div>
                )}
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
            <div className="composer">
              <input
                type="text"
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
              <button className="send" onClick={send} disabled={sending}>
                {sending ? "生成中" : "发送"}
              </button>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}

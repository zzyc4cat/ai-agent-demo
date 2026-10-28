export type Citation = {
  source: string;
  chunk_index?: number | null;
  snippet: string;
};

export type User = {
  id: number;
  username: string;
  role: "user" | "admin";
  tenant_id: string;
};

export type StoredMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  latency_ms?: number | null;
  refused?: number | boolean;
};

export type ConvSummary = {
  id: string;
  title: string;
  created_at: string;
  messages: number;
  pinned?: number;
};

export type StreamHandlers = {
  onMeta?: (d: { request_id: string; conversation_id: string }) => void;
  onCitations?: (c: Citation[]) => void;
  onToken?: (t: string) => void;
  onDone?: (d: { request_id: string; conversation_id: string; refused: boolean; latency_ms: number }) => void;
  onError?: (msg: string) => void;
};

let TOKEN = localStorage.getItem("kb_token") ?? "";

export function setToken(token: string): void {
  TOKEN = token;
  localStorage.setItem("kb_token", token);
}

export function clearToken(): void {
  TOKEN = "";
  localStorage.removeItem("kb_token");
}

export function hasToken(): boolean {
  return !!TOKEN;
}

function headers(json = false): Record<string, string> {
  const h: Record<string, string> = {};
  if (TOKEN) h.Authorization = `Bearer ${TOKEN}`;
  if (json) h["Content-Type"] = "application/json";
  return h;
}

async function failMessage(res: Response): Promise<string> {
  try {
    const data = await res.json();
    return data.detail ?? `请求失败（${res.status}）`;
  } catch {
    return `请求失败（${res.status}）`;
  }
}

export async function apiRegister(username: string, password: string): Promise<User> {
  const res = await fetch("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error(await failMessage(res));
  const data = await res.json();
  setToken(data.token);
  return data.user;
}

export async function apiLogin(username: string, password: string): Promise<User> {
  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error(await failMessage(res));
  const data = await res.json();
  setToken(data.token);
  return data.user;
}

export async function apiLogout(): Promise<void> {
  try {
    await fetch("/auth/logout", { method: "POST", headers: headers() });
  } finally {
    clearToken();
  }
}

export async function apiMe(): Promise<User | null> {
  if (!TOKEN) return null;
  try {
    const res = await fetch("/auth/me", { headers: headers() });
    return res.ok ? await res.json() : null;
  } catch {
    return null;
  }
}

export async function askStream(
  opts: { question: string; conversationId?: string | null },
  h: StreamHandlers,
): Promise<void> {
  const res = await fetch("/kb/stream", {
    method: "POST",
    headers: headers(true),
    body: JSON.stringify({ question: opts.question, conversation_id: opts.conversationId ?? null }),
  });
  if (!res.ok || !res.body) throw new Error(await failMessage(res));

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let idx: number;
    while ((idx = buffer.indexOf("\n\n")) >= 0) {
      const raw = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      dispatch(raw, h);
    }
  }
}

function dispatch(raw: string, h: StreamHandlers): void {
  let event = "message";
  let data = "";
  for (const line of raw.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) data += line.slice(5).trim();
  }
  if (!data) return;
  let parsed: any;
  try {
    parsed = JSON.parse(data);
  } catch {
    return;
  }
  if (event === "meta") h.onMeta?.(parsed);
  else if (event === "citations") h.onCitations?.(parsed.citations ?? []);
  else if (event === "token") h.onToken?.(parsed.text ?? "");
  else if (event === "done") h.onDone?.(parsed);
  else if (event === "error") h.onError?.(parsed.message ?? "生成失败");
}

export async function fetchConversations(): Promise<ConvSummary[]> {
  try {
    const res = await fetch("/kb/conversations", { headers: headers() });
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data.items) ? data.items : [];
  } catch {
    return [];
  }
}

export async function fetchConversation(id: string): Promise<StoredMessage[]> {
  try {
    const res = await fetch(`/kb/conversations/${id}`, { headers: headers() });
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data.messages) ? data.messages : [];
  } catch {
    return [];
  }
}

export async function patchConversation(
  id: string,
  payload: { title?: string; pinned?: boolean },
): Promise<boolean> {
  const res = await fetch(`/kb/conversations/${id}`, {
    method: "PATCH",
    headers: headers(true),
    body: JSON.stringify(payload),
  });
  return res.ok;
}

export async function deleteConversation(id: string): Promise<boolean> {
  const res = await fetch(`/kb/conversations/${id}`, { method: "DELETE", headers: headers() });
  return res.ok;
}

export async function sendFeedback(opts: {
  messageId: string;
  rating: "up" | "down";
  reason?: string;
}): Promise<void> {
  await fetch("/feedback", {
    method: "POST",
    headers: headers(true),
    body: JSON.stringify({
      message_id: opts.messageId,
      rating: opts.rating,
      reason: opts.reason ?? null,
    }),
  });
}

export type AdminDoc = {
  path: string;
  content_hash: string;
  chunk_count: number;
  updated_at: string;
  deleted_at?: string | null;
  exists: boolean;
  status: "active" | "deleted";
};

export type AdminAudit = {
  id: number;
  operator: string;
  action: string;
  target: string;
  detail?: string;
  created_at: string;
};

export async function fetchTenants(): Promise<string[]> {
  try {
    const res = await fetch("/health");
    if (!res.ok) return [];
    const data = await res.json();
    return Array.isArray(data.tenants) ? data.tenants : [];
  } catch {
    return [];
  }
}

export async function fetchAdminDocs(tenant: string): Promise<AdminDoc[]> {
  const res = await fetch(`/admin/docs?tenant=${encodeURIComponent(tenant)}`, { headers: headers() });
  if (!res.ok) throw new Error(await failMessage(res));
  const data = await res.json();
  return Array.isArray(data.items) ? data.items : [];
}

export async function fetchAudit(tenant: string): Promise<AdminAudit[]> {
  const res = await fetch(`/admin/audit?tenant=${encodeURIComponent(tenant)}`, { headers: headers() });
  if (!res.ok) throw new Error(await failMessage(res));
  const data = await res.json();
  return Array.isArray(data.items) ? data.items : [];
}

export type UsageTotal = {
  messages: number;
  prompt_tokens: number;
  completion_tokens: number;
  cost_cny: number | null;
};

export async function fetchUsage(tenant: string, days = 7): Promise<UsageTotal> {
  const res = await fetch(
    `/admin/usage?tenant=${encodeURIComponent(tenant)}&days=${days}`,
    { headers: headers() },
  );
  if (!res.ok) throw new Error(await failMessage(res));
  const data = await res.json();
  return data.total;
}

export async function deleteDoc(tenant: string, source: string): Promise<void> {
  const res = await fetch("/admin/docs/delete", {
    method: "POST",
    headers: headers(true),
    body: JSON.stringify({ tenant, source }),
  });
  if (!res.ok) throw new Error(await failMessage(res));
}

export async function restoreDoc(tenant: string, source: string): Promise<void> {
  const res = await fetch("/admin/docs/restore", {
    method: "POST",
    headers: headers(true),
    body: JSON.stringify({ tenant, source }),
  });
  if (!res.ok) throw new Error(await failMessage(res));
}

export type KbTask = {
  id: string;
  tenant_id: string;
  kind: string;
  target: string;
  status: string;
  message?: string;
  chunks: number;
};

export async function uploadDoc(tenant: string, file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file);
  form.append("tenant", tenant);
  const res = await fetch("/admin/docs/upload", {
    method: "POST",
    headers: headers(),
    body: form,
  });
  if (!res.ok) throw new Error(await failMessage(res));
  const data = await res.json();
  return data.task_id;
}

export async function importUrl(tenant: string, url: string): Promise<string> {
  const res = await fetch("/admin/docs/import_url", {
    method: "POST",
    headers: headers(true),
    body: JSON.stringify({ tenant, url }),
  });
  if (!res.ok) throw new Error(await failMessage(res));
  const data = await res.json();
  return data.task_id;
}

export async function fetchTask(id: string): Promise<KbTask> {
  const res = await fetch(`/admin/tasks/${id}`, { headers: headers() });
  if (!res.ok) throw new Error(await failMessage(res));
  return res.json();
}

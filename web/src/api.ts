export type Citation = {
  source: string;
  chunk_index?: number | null;
  snippet: string;
};

export type StreamHandlers = {
  onMeta?: (d: { request_id: string; tenant: string }) => void;
  onCitations?: (c: Citation[]) => void;
  onToken?: (t: string) => void;
  onDone?: (d: { request_id: string; refused: boolean; latency_ms: number }) => void;
  onError?: (msg: string) => void;
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

export async function askStream(
  opts: { question: string; apiKey: string; tenant: string },
  h: StreamHandlers,
): Promise<void> {
  const res = await fetch("/kb/stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": opts.apiKey,
      "X-Tenant": opts.tenant,
    },
    body: JSON.stringify({ question: opts.question }),
  });

  if (!res.ok || !res.body) {
    const map: Record<number, string> = {
      401: "密钥无效，请重新填写",
      404: "租户不存在",
      429: "请求太频繁，请稍后再试",
    };
    throw new Error(map[res.status] ?? `服务异常（${res.status}）`);
  }

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

export async function sendFeedback(opts: {
  messageId: string;
  rating: "up" | "down";
  reason?: string;
  apiKey: string;
  tenant: string;
}): Promise<void> {
  await fetch("/feedback", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": opts.apiKey,
      "X-Tenant": opts.tenant,
    },
    body: JSON.stringify({
      message_id: opts.messageId,
      rating: opts.rating,
      reason: opts.reason ?? null,
    }),
  });
}

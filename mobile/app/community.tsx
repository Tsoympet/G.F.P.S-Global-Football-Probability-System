import React, { useEffect, useRef, useState } from "react";
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform
} from "react-native";
import { useAuth } from "../auth/AuthContext";
import { api } from "../lib/api";
import { ScreenContainer } from "./components/ScreenContainer";
import { EmptyState } from "./components/EmptyState";

type ChatMessage = {
  id: string;
  author: string;
  text: string;
  ts: string;
  system?: boolean;
};

export default function CommunityScreen() {
  const { token, profile } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState<"connecting" | "open" | "closed">(
    "connecting"
  );

  const wsRef = useRef<WebSocket | null>(null);
  const listRef = useRef<FlatList<ChatMessage> | null>(null);

  // derive WS URL from API base
  const buildWsUrl = () => {
    const base = api.defaults.baseURL || "http://10.0.2.2:8000";
    const wsBase = base.replace(/^http/, "ws").replace(/\/+$/, "");
    const t = token ? encodeURIComponent(token) : "";
    return t ? `${wsBase}/ws/chat?token=${t}` : `${wsBase}/ws/chat`;
  };

  const appendMessage = (msg: ChatMessage) => {
    setMessages(prev => [...prev, msg]);
  };

  const connect = () => {
    if (!token) {
      setStatus("closed");
      return;
    }

    const url = buildWsUrl();
    setStatus("connecting");

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus("open");
        appendMessage({
          id: `sys-${Date.now()}`,
          author: "system",
          text: "Joined global predictions room.",
          ts: new Date().toISOString(),
          system: true
        });
      };

      ws.onmessage = event => {
        try {
          const data = JSON.parse(event.data);
          const author = data.author || "user";
          const text = data.text || "";
          const ts = data.ts || new Date().toISOString();

          if (!text) return;

          appendMessage({
            id: `msg-${Date.now()}-${Math.random()}`,
            author,
            text,
            ts
          });
        } catch (e) {
          // raw text fallback
          appendMessage({
            id: `msg-${Date.now()}-${Math.random()}`,
            author: "server",
            text: String(event.data),
            ts: new Date().toISOString()
          });
        }
      };

      ws.onerror = () => {
        setStatus("closed");
        appendMessage({
          id: `sys-${Date.now()}`,
          author: "system",
          text: "Connection error.",
          ts: new Date().toISOString(),
          system: true
        });
      };

      ws.onclose = () => {
        setStatus("closed");
        appendMessage({
          id: `sys-${Date.now()}`,
          author: "system",
          text: "Disconnected from chat.",
          ts: new Date().toISOString(),
          system: true
        });
      };
    } catch (err) {
      console.log("WS connect error", err);
      setStatus("closed");
    }
  };

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => {
    if (messages.length && listRef.current) {
      listRef.current.scrollToEnd({ animated: true });
    }
  }, [messages]);

  const sendMessage = () => {
    const ws = wsRef.current;
    const text = input.trim();
    if (!ws || status !== "open" || !text) return;

    const payload = {
      type: "chat_message",
      room: "global",
      text,
      author: profile?.display_name || profile?.email || "me",
      ts: new Date().toISOString()
    };

    try {
      ws.send(JSON.stringify(payload));
      appendMessage({
        id: `local-${Date.now()}`,
        author: "me",
        text,
        ts: payload.ts
      });
      setInput("");
    } catch (err) {
      console.log("WS send error", err);
    }
  };

  if (!token) {
    return (
      <ScreenContainer
        style={{
          alignItems: "center",
          justifyContent: "center"
        }}
      >
        <Text style={{ color: "#fff" }}>You need to login to join chat.</Text>
      </ScreenContainer>
    );
  }

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: "#000" }}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      keyboardVerticalOffset={80}
    >
      <ScreenContainer style={{ paddingBottom: 0 }}>
        <View style={{ marginBottom: 8 }}>
          <Text style={{ color: "#0f0", fontSize: 18, fontWeight: "700" }}>
            Global Predictions Room
          </Text>
          <Text style={{ color: "#777", fontSize: 12 }}>
            Status:{" "}
            {status === "connecting"
              ? "Connecting..."
              : status === "open"
              ? "Connected"
              : "Disconnected"}
          </Text>
        </View>

        <View style={{ flex: 1, marginBottom: 8 }}>
          {messages.length === 0 ? (
            <EmptyState message="No messages yet. Be the first to share a prediction." />
          ) : (
            <FlatList
              ref={ref => {
                listRef.current = ref;
              }}
              data={messages}
              keyExtractor={item => item.id}
              renderItem={({ item }) => (
                <View
                  style={{
                    paddingVertical: 4,
                    paddingHorizontal: 6
                  }}
                >
                  <Text
                    style={{
                      color: item.system
                        ? "#888"
                        : item.author === "me"
                        ? "#00ff88"
                        : "#fff",
                      fontWeight: item.system ? "400" : "600",
                      fontSize: 12
                    }}
                  >
                    {item.system ? "[system]" : item.author}
                  </Text>
                  <Text style={{ color: "#eee", fontSize: 14 }}>
                    {item.text}
                  </Text>
                </View>
              )}
            />
          )}
        </View>

        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            paddingVertical: 8
          }}
        >
          <TextInput
            style={{
              flex: 1,
              backgroundColor: "#111",
              borderWidth: 1,
              borderColor: "#333",
              borderRadius: 6,
              paddingHorizontal: 10,
              paddingVertical: 6,
              color: "#fff",
              marginRight: 8
            }}
            placeholder="Share your prediction..."
            placeholderTextColor="#666"
            value={input}
            onChangeText={setInput}
            onSubmitEditing={sendMessage}
          />
          <TouchableOpacity
            onPress={sendMessage}
            disabled={status !== "open" || !input.trim()}
            style={{
              backgroundColor:
                status === "open" && input.trim() ? "#00ff88" : "#333",
              paddingHorizontal: 12,
              paddingVertical: 8,
              borderRadius: 6
            }}
          >
            <Text
              style={{
                color:
                  status === "open" && input.trim() ? "#000" : "#777",
                fontWeight: "700"
              }}
            >
              Send
            </Text>
          </TouchableOpacity>
        </View>
      </ScreenContainer>
    </KeyboardAvoidingView>
  );
}

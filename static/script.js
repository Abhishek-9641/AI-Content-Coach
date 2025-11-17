document.addEventListener("DOMContentLoaded", () => {
  // --------------------- GLOBALS -------------------------
  window.chatHistory = [];

  // --------------------- CHAT FUNCTIONALITY -------------------------
  const sendBtn = document.getElementById("send-btn");
  const userInput = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");

  if (sendBtn && userInput) {
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", e => {
      if (e.key === "Enter") sendMessage();
    });
  } else {
    console.warn("⚠️ Send button or user input not found!");
  }

  function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage("user", text);
    userInput.value = "";

    fetch("/agent_query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    })
      .then(res => res.json())
      .then(data => addMessage("agent", data.result || "⚠️ No response from agent."))
      .catch(() => addMessage("agent", "❌ Error contacting agent."));
  }

  function addMessage(sender, message) {
    if (!chatBox) return;

    const msgDiv = document.createElement("div");
    msgDiv.classList.add(sender === "user" ? "user-msg" : "agent-msg");
    msgDiv.innerHTML = message
      .replace(/\n/g, "<br>")
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/(\d+)\.\s/g, "<br><strong>$1.</strong> ");

    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    // ------------------ PUSH TO CHAT HISTORY ------------------
    if (sender === "user") {
      window.chatHistory.push([message, ""]);
    } else {
      if (window.chatHistory.length > 0) {
        window.chatHistory[window.chatHistory.length - 1][1] = message;
      } else {
        window.chatHistory.push(["", message]);
      }
    }
  }

  // --------------------- CHAT EXPORTER -------------------------
  const exportBtn = document.getElementById("export-chat-btn");
  if (exportBtn) {
    exportBtn.addEventListener("click", async () => {
      try {
        const chatHistory = window.chatHistory || [];
        if (chatHistory.length === 0) {
          alert("⚠️ No chat history to export.");
          return;
        }

        const response = await fetch("/export_chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ chat_history: chatHistory })
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `chat_export_${new Date().toISOString().replace(/[:.]/g, "-")}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        console.log("✅ Chat exported successfully!");
      } catch (error) {
        console.error("❌ Export failed:", error);
        alert("❌ Failed to export chat. Check console for details.");
      }
    });
  } else console.warn("⚠️ Export chat button not found!");

  // --------------------- INGEST FUNCTIONALITY -------------------------
  const ingestPdfBtn = document.getElementById("ingest-pdf");
  const ingestUrlBtn = document.getElementById("ingest-url");
  const clearIngestedBtn = document.getElementById("clear-ingested");

  if (ingestPdfBtn) ingestPdfBtn.addEventListener("click", ingestContent);
  if (ingestUrlBtn) ingestUrlBtn.addEventListener("click", ingestContent);
  if (clearIngestedBtn) clearIngestedBtn.addEventListener("click", clearIngested);

  function ingestContent() {
    const pdfInput = document.getElementById("pdf-upload");
    const urlInput = document.getElementById("url-input");
    const formData = new FormData();

    if (pdfInput && pdfInput.files.length > 0) {
      formData.append("pdf_file", pdfInput.files[0]);
    } else if (urlInput && urlInput.value.trim() !== "") {
      formData.append("url", urlInput.value.trim());
    } else {
      alert("⚠️ Please upload a PDF or enter a URL first.");
      return;
    }

    const statusEl = document.getElementById("ingest-status");
    const summaryEl = document.getElementById("ingest-summary");
    if (statusEl) statusEl.textContent = "";
    if (summaryEl) summaryEl.textContent = "";

    fetch("/ingest", { method: "POST", body: formData })
      .then(res => res.json())
      .then(data => {
        if (!statusEl || !summaryEl) return;
        if (data.status === "error") {
          statusEl.textContent = "❌ " + data.message;
          statusEl.className = "error";
          summaryEl.textContent = "";
        } else {
          statusEl.textContent = "✅ " + (data.message_type || "Content successfully ingested!");
          statusEl.className = "success";
          summaryEl.textContent = data.summary_snippet || "";
        }
      })
      .catch(() => {
        if (statusEl) {
          statusEl.textContent = "❌ Failed to ingest file or URL.";
          statusEl.className = "error";
        }
        if (summaryEl) summaryEl.textContent = "";
      });
  }

  function clearIngested() {
    fetch("/clear-ingested", { method: "POST" })
      .then(res => res.json())
      .then(data => {
        const statusEl = document.getElementById("ingest-status");
        const summaryEl = document.getElementById("ingest-summary");
        if (!statusEl) return;

        if (data.status === "success") {
          statusEl.textContent = data.message;
          statusEl.className = "success";
          if (summaryEl) summaryEl.textContent = "";
        } else {
          statusEl.textContent = "❌ Failed to clear ingested data.";
          statusEl.className = "error";
        }
      })
      .catch(() => {
        const statusEl = document.getElementById("ingest-status");
        if (statusEl) {
          statusEl.textContent = "❌ Failed to clear ingested data.";
          statusEl.className = "error";
        }
      });
  }

  // ----------------- CLEAR CHAT -----------------------
  const clearChatBtn = document.getElementById("clear-chat-btn");
  if (clearChatBtn) {
    clearChatBtn.addEventListener("click", () => {
      if (chatBox) chatBox.innerHTML = "";
      window.chatHistory = [];
    });
  } else console.warn("⚠️ Clear chat button not found!");

  // ----------------- VOICE INPUT -----------------------
  const micBtn = document.getElementById("mic-btn");
  let mediaRecorder, audioChunks = [], isRecording = false;

  if (micBtn) {
    micBtn.addEventListener("click", async () => {
      if (!isRecording) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          mediaRecorder = new MediaRecorder(stream);
          audioChunks = [];

          mediaRecorder.ondataavailable = e => {
            if (e.data.size > 0) audioChunks.push(e.data);
          };

          mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            const formData = new FormData();
            formData.append("audio", audioBlob, "input.wav");

            const response = await fetch("/transcribe_audio", { method: "POST", body: formData });
            const data = await response.json();

            if (data.text) {
              userInput.value = data.text;
              sendMessage();
            } else {
              alert("❌ Transcription failed: " + (data.error || "Unknown error"));
            }

            micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
            isRecording = false;
          };

          mediaRecorder.start();
          micBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';
          isRecording = true;
        } catch (err) {
          console.error("Microphone access error:", err);
          alert("🎤 Microphone access denied or unavailable.");
        }
      } else {
        mediaRecorder.stop();
      }
    });
  } else console.warn("⚠️ Mic button not found!");

  // ----------------- CONTENT GROWTH -----------------------
  const analyzeBtn = document.getElementById("analyze-btn");
  if (analyzeBtn) {
    analyzeBtn.addEventListener("click", async () => {
      const postUrl = document.getElementById("post-url").value;
      const caption = document.getElementById("caption").value;
      const metricsInput = document.getElementById("metrics").value;
      const screenshotFile = document.getElementById("media-upload").files[0];
      const outputDiv = document.getElementById("analysis-result");

      if (!outputDiv) return;
      outputDiv.innerHTML = "<p>⏳ Analyzing content, please wait...</p>";

      const formData = new FormData();
      if (postUrl) formData.append("post_url", postUrl);
      if (caption) formData.append("caption", caption);
      if (metricsInput) formData.append("metrics", metricsInput);
      if (screenshotFile) formData.append("screenshot", screenshotFile);

      try {
        const response = await fetch("/content_growth", { method: "POST", body: formData });
        const data = await response.json();

        if (data.error) {
          outputDiv.innerHTML = `<p style="color:red;">❌ Error: ${data.error}</p>`;
          return;
        }

        outputDiv.innerHTML = `
          <h3>Metrics:</h3>
          <pre>${JSON.stringify(data.metrics, null, 2)}</pre>
          <h3>Advice:</h3>
          <p>${data.advice}</p>
          <h3>SEO Suggestions:</h3>
          <p>${data.seo}</p>
          <h3>Social Media Optimization:</h3>
          <p>${data.social}</p>
        `;
      } catch (err) {
        console.error(err);
        outputDiv.innerHTML = "<p style='color:red;'>❌ Failed to analyze content growth.</p>";
      }
    });
  } else console.warn("⚠️ Analyze button not found!");

  // ----------------- TEXT TO SPEECH -----------------------
  const ttsChatBtn = document.getElementById("tts-chat-btn");
  if (ttsChatBtn) {
    ttsChatBtn.addEventListener("click", () => {
      const chatHistory = window.chatHistory || [];
      if (chatHistory.length === 0) {
        alert("⚠️ No chat history to read.");
        return;
      }

      const combinedText = chatHistory.map(([user, agent], i) =>
        `Exchange ${i + 1}: User said: ${user}. Agent replied: ${agent}.`
      ).join(" ");

      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(combinedText);
        utterance.rate = 1;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
      } else {
        alert("⚠️ Your browser does not support Text-to-Speech.");
      }
    });
  } else console.warn("⚠️ TTS button not found!");
});

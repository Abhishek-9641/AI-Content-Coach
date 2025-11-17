document.addEventListener("DOMContentLoaded", () => {

  // --------------------- CHAT FUNCTIONALITY -------------------------

  // Initialize global chat history
  window.chatHistory = [];

  document.getElementById("send-btn").addEventListener("click", sendMessage);
  document.getElementById("user-input").addEventListener("keypress", function(e) {
    if (e.key === "Enter") sendMessage();
  });

  function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    addMessage("user", text);  // Display user message and track
    input.value = "";

    fetch("/agent_query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    })
    .then(res => res.json())
    .then(data => {
      addMessage("agent", data.result || "⚠️ No response from agent.");  // Display agent message and track
    })
    .catch(() => addMessage("agent", "❌ Error contacting agent."));
  }

  function addMessage(sender, message) {
    const chatBox = document.getElementById("chat-box");
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
      // Start a new chat entry with user's message
      window.chatHistory.push([message, ""]);
    } else {
      // Update the last entry with agent's reply
      if (window.chatHistory.length > 0) {
        window.chatHistory[window.chatHistory.length - 1][1] = message;
      } else {
        // Fallback if agent message comes first
        window.chatHistory.push(["", message]);
      }
    }
  }




  // works!!
  // document.getElementById("send-btn").addEventListener("click", sendMessage);
  // document.getElementById("user-input").addEventListener("keypress", function(e) {
  //   if (e.key === "Enter") sendMessage();
  // });

  // function sendMessage() {
  //   const input = document.getElementById("user-input");
  //   const text = input.value.trim();
  //   if (!text) return;

  //   addMessage("user", text);
  //   input.value = "";

  //   fetch("/agent_query", {
  //     method: "POST",
  //     headers: { "Content-Type": "application/json" },
  //     body: JSON.stringify({ text })
  //   })
  //   .then(res => res.json())
  //   .then(data => {
  //     addMessage("agent", data.result || "⚠️ No response from agent.");
  //   })
  //   .catch(() => addMessage("agent", "❌ Error contacting agent."));
  // }

  // function addMessage(sender, message) {
  //   const chatBox = document.getElementById("chat-box");
  //   const msgDiv = document.createElement("div");
  //   msgDiv.classList.add(sender === "user" ? "user-msg" : "agent-msg");
  //   msgDiv.innerHTML = message
  //     .replace(/\n/g, "<br>")
  //     .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
  //     .replace(/(\d+)\.\s/g, "<br><strong>$1.</strong> ");

  //   chatBox.appendChild(msgDiv);
  //   chatBox.scrollTop = chatBox.scrollHeight;
  // }

  
  // --------------------- CHAT EXPORTER FUNCTIONALITY -------------------------

  document.getElementById("export-chat-btn").addEventListener("click", async () => {
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

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

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



  // ---------------- INGEST FUNCTIONALITY ----------------

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

    // Clear previous status/summary
    statusEl.textContent = "";
    statusEl.className = "";
    summaryEl.textContent = "";

    fetch("/ingest", { method: "POST", body: formData })
      .then(res => res.json())
      .then(data => {
        if (data.status === "error") {
          statusEl.textContent = "❌ " + data.message;
          statusEl.className = "error";
          summaryEl.textContent = "";
        } else {
          // Green success message
          statusEl.textContent = "✅ " + (data.message_type || "Content successfully ingested!");
          statusEl.className = "success";

          // Display summary snippet separately
          summaryEl.textContent = data.summary_snippet || "";
          console.log("Summary snippet:", data.summary_snippet);
        }
      })
      .catch(() => {
        statusEl.textContent = "❌ Failed to ingest file or URL.";
        statusEl.className = "error";
        summaryEl.textContent = "";
      });
  }


// function clearIngested() {
//   fetch("/clear-ingested", { method: "POST" })
//     .then(res => res.json())
//     .then(data => {
//       const statusEl = document.getElementById("ingest-status");
//       const summaryEl = document.getElementById("ingest-summary");

//       if (data.status === "success") {
//         statusEl.textContent = "✅ Ingested data cleared.";
//         statusEl.className = "success";
//         summaryEl.textContent = "";
//       } else {
//         statusEl.textContent = "❌ Failed to clear ingested data.";
//         statusEl.className = "error";
//       }
//     })
//     .catch(() => {
//       const statusEl = document.getElementById("ingest-status");
//       statusEl.textContent = "❌ Failed to clear ingested data.";
//       statusEl.className = "error";
//     });
// }



//  WORKING TOO!!
// const ingestPdfBtn = document.getElementById("ingest-pdf");
// const ingestUrlBtn = document.getElementById("ingest-url");
// const clearIngestedBtn = document.getElementById("clear-ingested");

// if (ingestPdfBtn) ingestPdfBtn.addEventListener("click", ingestContent);
// if (ingestUrlBtn) ingestUrlBtn.addEventListener("click", ingestContent);
// if (clearIngestedBtn) clearIngestedBtn.addEventListener("click", clearIngested);

// function ingestContent() {
//   const pdfInput = document.getElementById("pdf-upload");
//   const urlInput = document.getElementById("url-input");
//   const formData = new FormData();

//   if (pdfInput && pdfInput.files.length > 0) {
//     formData.append("pdf_file", pdfInput.files[0]);
//   } else if (urlInput && urlInput.value.trim() !== "") {
//     formData.append("url", urlInput.value.trim());
//   } else {
//     alert("⚠️ Please upload a PDF or enter a URL first.");
//     return;
//   }

//   const statusEl = document.getElementById("ingest-status");
//   const previewEl = document.getElementById("ingest-preview");

//   // Clear previous content
//   statusEl.textContent = "";
//   previewEl.textContent = "";

//   fetch("/ingest", { method: "POST", body: formData })
//     .then(res => res.json())
//     .then(data => {
//       if (data.status === "error") {
//         statusEl.textContent = "❌ " + data.message;
//         statusEl.className = "error"; // add CSS class
//         previewEl.textContent = "";
//       } else {
//         // Only show a simple success message in status
//         statusEl.textContent = data.status === "success" && formData.has("pdf_file")
//           ? "✅ PDF successfully ingested!"
//           : "✅ URL successfully ingested!";
//         statusEl.className = "success";

//         // Show the summary snippet in a separate element
//         previewEl.textContent = data.content_preview || "";
//         previewEl.id = "ingest-summary";

//         console.log("Preview of ingested content:", data.content_preview);
//       }
//     })
//     .catch(() => {
//       statusEl.textContent = "❌ Failed to ingest file or URL.";
//       statusEl.className = "error";
//       previewEl.textContent = "";
//     });
// }




  // Working!!
  // const ingestPdfBtn = document.getElementById("ingest-pdf");
  // const ingestUrlBtn = document.getElementById("ingest-url");
  // const clearIngestedBtn = document.getElementById("clear-ingested");

  // if (ingestPdfBtn) ingestPdfBtn.addEventListener("click", ingestContent);
  // if (ingestUrlBtn) ingestUrlBtn.addEventListener("click", ingestContent);
  // if (clearIngestedBtn) clearIngestedBtn.addEventListener("click", clearIngested);

  // function ingestContent() {
  //   const pdfInput = document.getElementById("pdf-upload");
  //   const urlInput = document.getElementById("url-input");
  //   const formData = new FormData();

  //   if (pdfInput && pdfInput.files.length > 0) {
  //     formData.append("pdf_file", pdfInput.files[0]);
  //   } else if (urlInput && urlInput.value.trim() !== "") {
  //     formData.append("url", urlInput.value.trim());
  //   } else {
  //     alert("⚠️ Please upload a PDF or enter a URL first.");
  //     return;
  //   }

  //   const statusEl = document.getElementById("ingest-status");
  //   const previewEl = document.getElementById("ingest-preview");

  //   statusEl.textContent = "";
  //   previewEl.textContent = "";

  //   fetch("/ingest", { method: "POST", body: formData })
  //     .then(res => res.json())
  //     .then(data => {
  //       if (data.status === "error") {
  //         statusEl.textContent = "❌ " + data.message;
  //         statusEl.style.color = "red";
  //         previewEl.textContent = "";
  //       } else {
  //         statusEl.textContent = "✅ " + data.message;
  //         statusEl.style.color = "green";
  //         previewEl.textContent = data.content_preview || "";
  //         console.log("Preview of ingested content:", data.content_preview);
  //       }
  //     })
  //     .catch(() => {
  //       statusEl.textContent = "❌ Failed to ingest file or URL.";
  //       statusEl.style.color = "red";
  //       previewEl.textContent = "";
  //     });
  // }


  // ----------------- Clear ingested data -----------------------
  function clearIngested() {
    fetch("/clear-ingested", { method: "POST" })
      .then(res => res.json())
      .then(data => {
        const statusEl = document.getElementById("ingest-status");
        const summaryEl = document.getElementById("ingest-summary");
        
        if (data.status === "success") {
          statusEl.textContent = data.message;
          statusEl.className = "success";  // apply green style
          summaryEl.textContent = "";       // clear the summary snippet
        } else {
          statusEl.textContent = "❌ Failed to clear ingested data.";
          statusEl.className = "error"; 
        }
      })
      .catch(() => {
        const statusEl = document.getElementById("ingest-status");
        statusEl.textContent = "❌ Failed to clear ingested data.";
        statusEl.className = "error"; 
      });
  }


  // ---------------- CLEAR CHAT ----------------
  const clearChatBtn = document.getElementById("clear-chat-btn");
  if (clearChatBtn) {
    clearChatBtn.addEventListener("click", () => {
      const chatBox = document.getElementById("chat-box");
      chatBox.innerHTML = "";
    });
  }


  // ---------------- VOICE INPUT USING OPENAI WHISPER ----------------
  const micBtn = document.getElementById("mic-btn");
  let mediaRecorder;
  let audioChunks = [];
  let isRecording = false;

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

            const response = await fetch("/transcribe_audio", {
              method: "POST",
              body: formData
            });

            const data = await response.json();
            if (data.text) {
              document.getElementById("user-input").value = data.text; 
              //  ----------> Use sendMessage() to send the voice to be sent automatically to the agent without having to press send
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
  }


  // ---------------- Content Growth Analysis ----------------
  const analyzeBtn = document.getElementById("analyze-btn");

  if (analyzeBtn) {
    analyzeBtn.addEventListener("click", async () => {
      const postUrl = document.getElementById("post-url").value;
      const caption = document.getElementById("caption").value;
      const metricsInput = document.getElementById("metrics").value;
      const screenshotFile = document.getElementById("media-upload").files[0];

      const formData = new FormData();
      if (postUrl) formData.append("post_url", postUrl);
      if (caption) formData.append("caption", caption);
      if (metricsInput) formData.append("metrics", metricsInput);
      if (screenshotFile) formData.append("screenshot", screenshotFile);

      // Show loading message
      const outputDiv = document.getElementById("analysis-result");
      outputDiv.innerHTML = "<p>⏳ Analyzing content, please wait...</p>";

      try {
        const response = await fetch("/content_growth", {
          method: "POST",
          body: formData
        });

        const data = await response.json();

        if (data.error) {
          outputDiv.innerHTML = `<p style="color:red;">❌ Error: ${data.error}</p>`;
          return;
        }

        // Display structured report
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
  }


  // ---------------- TEXT TO SPEECH FUNCTIONALITY ----------------

  const ttsChatBtn = document.getElementById("tts-chat-btn");

  if (ttsChatBtn) {
    ttsChatBtn.addEventListener("click", () => {
      const chatHistory = window.chatHistory || [];
      
      if (chatHistory.length === 0) {
        alert("⚠️ No chat history to read.");
        return;
      }

      // Combine chat messages into a single string
      const combinedText = chatHistory.map(([user, agent], i) => {
        return `Exchange ${i+1}: User said: ${user}. Agent replied: ${agent}.`;
      }).join(" ");

      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(combinedText);
        utterance.rate = 1;        // normal speed
        utterance.pitch = 1;       // normal pitch
        window.speechSynthesis.speak(utterance);
      } else {
        alert("⚠️ Your browser does not support Text-to-Speech.");
      }
    });
  }


})


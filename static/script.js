document.addEventListener("DOMContentLoaded", function () {
    let recording = false;
    let mediaRecorder;
    let audioChunks = [];
  
    document.getElementById("mic-button").addEventListener("click", () => {
      if (!recording) {
        startRecording();
      } else {
        stopRecording();
      }
    });
  
    document.getElementById("sendBtn").addEventListener("click", function () {
      const text = document.getElementById("textInput").value.trim();
      if (text) {
        sendMessage(text);
        document.getElementById("textInput").value = "";
      }
    });
  
    document.getElementById("textInput").addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        document.getElementById("sendBtn").click();
      }
    });
  
    document.getElementById("toggle-theme").addEventListener("change", function () {
      document.body.classList.toggle("light-mode", this.checked);
    });
  
    function startRecording() {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          mediaRecorder = new MediaRecorder(stream);
          audioChunks = [];
  
          mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
              audioChunks.push(event.data);
            }
          };
  
          mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
  
            fetch("/speech-to-text", {
              method: "POST",
              body: audioBlob
            })
              .then(res => res.json())
              .then(data => {
                sendMessage(data.text);
              });
          };
  
          mediaRecorder.start();
          recording = true;
          document.getElementById("mic-button").classList.add("recording");
        })
        .catch(error => {
          console.error("Microphone access denied:", error);
        });
    }
  
    function stopRecording() {
      if (mediaRecorder && recording) {
        mediaRecorder.stop();
        recording = false;
        document.getElementById("mic-button").classList.remove("recording");
      }
    }
  
    function sendMessage(messageText) {
      const voice = document.getElementById("voice").value;
  
      const userMessageElem = document.createElement("div");
      userMessageElem.className = "message user-message";
      userMessageElem.innerText = messageText;
  
      const row = document.createElement("div");
      row.className = "message-row";
      row.appendChild(userMessageElem);
      document.getElementById("chatContainer").appendChild(row);
  
      fetch("/process-message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userMessage: messageText, voice: voice })
      })
        .then(res => res.json())
        .then(data => {
          const botMsg = document.createElement("div");
          botMsg.className = "message bot-message";
          botMsg.innerText = data.openaiResponseText;
  
          const row = document.createElement("div");
          row.className = "message-row";
          row.appendChild(botMsg);
          document.getElementById("chatContainer").appendChild(row);
  
          if (data.openaiResponseSpeech) {
            playAudio(data.openaiResponseSpeech);
          }
        });
    }
  
    function playAudio(base64Audio) {
      if (!base64Audio || base64Audio.length < 50) {
        console.error("Invalid or empty audio");
        return;
      }
  
      const audio = new Audio("data:audio/wav;base64," + base64Audio);
      audio.load();
      audio.play().catch(err => {
        console.error("Playback failed:", err);
      });
    }
  });
  
import React from "react";

const ChatMessage = ({ text, sender }) => (
  <div className={`mb-3 flex ${sender === "user" ? "justify-end" : "justify-start"}`}>
    <div
      className={`max-w-[85%] p-2 rounded-lg break-words whitespace-pre-wrap ${
        sender === "user"
          ? "bg-[#0077B6] text-white rounded-br-none"
          : "bg-gray-200 text-gray-800 rounded-bl-none"
      }`}
    >
      {text}
    </div>
  </div>
);

export default ChatMessage;

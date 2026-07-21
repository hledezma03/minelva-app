import React from "react";
import ChatMessage from "./ChatMessage";
import { useChatbot } from "./useChatbot";

const ChatWindow = ({ onClose, chatbot }) => {
  const { messages, inputValue, setInputValue, isLoading, handleSendMessage, handleKeyPress } = chatbot;

  return (
    <div className="fixed bottom-24 right-6 w-80 h-96 bg-white rounded-xl shadow-2xl flex flex-col z-50 border border-gray-200 overflow-hidden">
      {/* Cabecera */}
      <div className="bg-[#0077B6] text-white p-3 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span>💧</span>
          <span className="font-semibold">Asistente Minelva</span>
        </div>
        <button onClick={onClose} className="text-white hover:text-gray-200">
          ✕
        </button>
      </div>

      {/* Área de mensajes */}
      <div className="flex-1 p-3 overflow-y-auto bg-gray-50">
        {messages.map((msg, index) => (
          <ChatMessage key={index} text={msg.text} sender={msg.sender} />
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-800 p-2 rounded-lg rounded-bl-none">
              <div className="flex gap-1">
                <span className="animate-bounce">●</span>
                <span className="animate-bounce delay-100">●</span>
                <span className="animate-bounce delay-200">●</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Campo de entrada */}
      <div className="border-t p-2 flex gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Escribe tu mensaje..."
          className="flex-1 p-2 border rounded-lg focus:outline-none focus:border-[#0077B6]"
          disabled={isLoading}
        />
        <button
          onClick={handleSendMessage}
          className="bg-[#0077B6] text-white px-3 py-2 rounded-lg hover:bg-[#005f8f] transition"
          disabled={isLoading}
        >
          Enviar
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;

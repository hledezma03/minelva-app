import React from "react";
import ChatWindow from "./ChatWindow";
import { useChatbot } from "./useChatbot";

const Chatbot = () => {
  const chatbot = useChatbot();

  return (
    <>
      {/* Botón flotante del chatbot */}
      <button
        onClick={chatbot.toggleChat}
        className="fixed bottom-6 right-6 bg-[#0077B6] text-white p-4 rounded-full shadow-lg hover:bg-[#005f8f] transition z-50"
      >
        💬
      </button>

      {/* Ventana del chatbot */}
      {chatbot.isOpen && <ChatWindow onClose={chatbot.toggleChat} chatbot={chatbot} />}
    </>
  );
};

export default Chatbot;

import React, { useState } from "react";
import { sendChatMessage } from "../api";

const ChatbotPage = () => {
    const [query, setQuery] = useState("");
    const [chatHistory, setChatHistory] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSend = async (message) => {
        const userId = localStorage.getItem("user_id");
        if (!userId) {
            alert("Please log in first.");
            return;
        }

        // Add user message to chat history
        const newChat = [...chatHistory, { sender: "user", text: message }];
        setChatHistory(newChat);
        setQuery("");
        setLoading(true);

        // Fetch AI response
        const data = await sendChatMessage(userId, message);
        const aiResponse = data?.response || "No response from AI.";

        // Add AI response to chat history
        setChatHistory([...newChat, { sender: "ai", text: aiResponse }]);
        setLoading(false);
    };

    const handleQuickReply = async (quickQuery) => {
        setQuery(quickQuery);
        await handleSend(quickQuery);
    };

    return (
        <div style={{ textAlign: "center", padding: "20px" }}>
            <h1>🤖 AI Sustainability Advisor</h1>
            <p>Ask about sustainable habits, eco-friendly choices, and carbon footprint reduction!</p>

            {/* Chat history display */}
            <div style={{
                height: "300px",
                overflowY: "auto",
                border: "1px solid #ccc",
                padding: "10px",
                marginBottom: "10px"
            }}>
                {chatHistory.map((msg, index) => (
                    <p key={index} style={{ textAlign: msg.sender === "user" ? "right" : "left" }}>
                        <strong>{msg.sender === "user" ? "You: " : "AI: "}</strong> {msg.text}
                    </p>
                ))}
                {loading && <p><em>AI is typing...</em></p>}
            </div>

            {/* User input */}
            <input 
                type="text" 
                placeholder="Ask AI a question..." 
                value={query} 
                onChange={(e) => setQuery(e.target.value)}
            />
            <button onClick={() => handleSend(query)} disabled={loading}>Ask AI</button>

            {/* Quick reply options */}
            {chatHistory.length > 0 && chatHistory[chatHistory.length - 1].sender === "ai" && (
                <div style={{ marginTop: "10px" }}>
                    <p>🤔 Choose a topic to continue:</p>
                    <button onClick={() => handleQuickReply("Tell me about electric vehicles.")}>🚗 EVs</button>
                    <button onClick={() => handleQuickReply("How do I reduce plastic waste?")}>♻️ Plastic Waste</button>
                    <button onClick={() => handleQuickReply("What are some energy-saving tips?")}>💡 Energy Savings</button>
                </div>
            )}
        </div>
    );
};

export default ChatbotPage;

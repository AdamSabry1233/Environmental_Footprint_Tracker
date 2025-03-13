import React, { useState } from "react";
import { sendChatMessage } from "../api";

const Chatbot = ({ userId }) => {
    const [query, setQuery] = useState("");
    const [response, setResponse] = useState("");

    const handleSendMessage = async () => {
        if (query.trim() === "") return;
        const data = await sendChatMessage(userId, query);
        setResponse(data?.response || "No response from AI.");
        setQuery("");
    };

    return (
        <div>
            <h2>AI Chatbot</h2>
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about sustainability..."
            />
            <button onClick={handleSendMessage}>Send</button>
            {response && <p>Bot: {response}</p>}
        </div>
    );
};

export default Chatbot;

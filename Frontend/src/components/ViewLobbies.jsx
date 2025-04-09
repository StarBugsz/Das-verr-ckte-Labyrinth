import React from 'react';
import useStore from "../StageManagement.jsx";
import "../index.css";
import {useNavigate} from "react-router-dom";
import {useWebSocket} from "../WebSocketProvider.jsx";

function ViewLobbies() {
    const lobbies = useStore((state) => state.LOBBY_LIST);
    const navigate = useNavigate(); // Navigations-Hook initialisieren
    const socket = useWebSocket();

    //Stellt die Funktion bereit, direkt über der button in die Lobby zu joinen
    const joinLobby = (lobbyLink) => {
        socket.send("join_lobby:" +lobbyLink);
        navigate(`/lobby/${lobbyLink}`);  // Navigiert zur Lobby-Seite
    };

    return (
        <div className="lobbys-container">
            <h1>Verfügbare Lobbys</h1>
            {Object.keys(lobbies).length > 0 ? (
                <div className="lobbys-list">
                    {Object.entries(lobbies).map(([key, value]) => {
                        const lobbyData = JSON.parse(value);
                        return (
                            <div key={key} className="lobbys-item">
                                <h3>Host: {lobbyData.host.name}</h3>
                                <p>Verfügbare
                                    Plätze: {lobbyData.size - Object.keys(lobbyData.players).length}/{lobbyData.size}</p>
                                <p>Join link: {window.location.origin}/lobby/{lobbyData.link}</p>
                                <button
                                    className="button-join"
                                    onClick={() => joinLobby(lobbyData.link)}
                                >
                                    Zur Lobby beitreten
                                </button>
                            </div>
                        );
                    })}
                </div>
            ) : (
                <p>Aktuell keine Lobbys verfügbar.</p>
            )}
        </div>
    );
}

export default ViewLobbies;

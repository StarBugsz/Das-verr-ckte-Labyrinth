import React, {useState, useMemo, useEffect} from 'react';
import "../index.css";
import useStore from "../StageManagement.jsx";
import {useWebSocket} from "../WebSocketProvider.jsx";
import {useNavigate, useParams} from "react-router-dom";

function CreateLobby({username}) {

    const [URL, setURL] = useState('');


    const lobbysize = useStore((state) => state.lobbysize);
    const boardSize = useStore((state) => state.boardSize);
    const privateLobby = useStore((state) => state.privateLobby);
    // const [playerCount, setPlayerCount] = useState(4);
    // const [boardSize, setBoardSize] = useState("7x7");
    // const [privateLobby, setPrivateLobby] = useState(false);

    const [copied, setCopied] = useState(false); // Für die "Kopiert!"-Meldung
    const navigate = useNavigate();
    const setLOBBYLINK = useStore(state => state.setLOBBYLINK);
    const setComingFromLobby = useStore(state => state.setComingFromLobby);

    const LOBBYLINK = useStore((state) => state.LOBBYLINK);
    const LOBBY_PARTICIPANTS = useStore(state => state.LOBBY_PARTICIPANTS);
    const socket = useWebSocket();
    const {lobbyId} = useParams();

    useEffect(() => {
        if (useStore.getState().UID === ``) {
            setLOBBYLINK(lobbyId);
            setComingFromLobby(true); // Herkunft setzen
            navigate('/');
        }
    }, [navigate]);

    // Kombiniert `host` und `players` in eine Liste, um dann alle Spieler in der Lobby anzeigen zu können
    const players = useMemo(() => {
        if (!LOBBY_PARTICIPANTS) return [];

        const otherPlayers = LOBBY_PARTICIPANTS.players
            ? Object.values(LOBBY_PARTICIPANTS.players)
            : [];
        return [...otherPlayers];
    }, [LOBBY_PARTICIPANTS]);


    //Vollständige URL speichern aus LOBBYLINK, welcher aus dem Backend kommt
    const createLobbyLink = () => {
        const url = `${window.location.origin}/lobby/${LOBBYLINK}`;
        setURL(url);

        // Link sofort in die Zwischenablage kopieren
        navigator.clipboard.writeText(url).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000); // Meldung nach 2 Sekunden entfernen
        });
    };

    //Link in die Zwischenablage kopieren (beim Klick auf den Link)
    const copyToClipboard = (e) => {
        e.preventDefault(); // Verhindert das Öffnen des Links
        if (URL) {
            navigator.clipboard.writeText(URL).then(() => {
                setCopied(true);
                setTimeout(() => setCopied(false), 2000); // Meldung nach 2 Sekunden entfernen
            });
        }
    };

    // KI-Spieler hinzufügen
    const addAIPlayer = () => {
        socket.send("add_ai_player");
    };

    // Spieler entfernen
    const handleKickPlayer = (nummer) => {
        socket.send("kick_player:" + nummer);
    };

    // Spiel starten
    const startGame = () => {
        socket.send("start_game");
    };


    if (!useStore.getState().IsLobbyCreator) {
        return (
            <div className="lobby-container">
                <h2 className="lobby-title">Lobby erstellen</h2>

                {/* Teilnehmerliste */}
                <div className="lobby-participants">
                    <strong>Lobby Teilnehmer:</strong>
                    <ul className="lobby-list">
                        {players.map((player, index) => (
                            <li key={index} className="lobby-list-item">
                                {player.name}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Lobby-Aktionen */}
                <div className="lobby-buttons">
                    <button className="button-elegante" onClick={createLobbyLink}>
                        Lobby-Link generieren
                    </button>
                </div>

                <div className="lobby-link-container">
                    {URL && (
                        <div>
                            <p className="lobby-link">
                                <a
                                    href="#"
                                    onClick={copyToClipboard}
                                >
                                    {URL}
                                </a>
                            </p>
                            {copied && <p className="copy-feedback">Kopiert!</p>}

                        </div>
                    )}
                </div>
            </div>
        );
    } else {
        return (
            <div className="lobby-container">
                <h2 className="lobby-title">Lobby erstellen</h2>

                {/* Formular für Lobby-Einstellungen */}
                <div className="lobby-form">
                    <div className="form-row">
                        <label htmlFor="lobbysize" className="lobby-text">Spieleranzahl:</label>
                        <select
                            id="lobbysize"
                            value={lobbysize}
                            onChange={(e) => {
                                const newValue = e.target.value; // Den neuen Wert erfassen
                                socket.send("settings:lobbysize:" + newValue.toString());
                            }}
                        >
                            <option value={2}>2</option>
                            <option value={3}>3</option>
                            <option value={4}>4</option>
                        </select>
                    </div>

                    <div className="lobby-hidden">
                        <label htmlFor="boardSize" className="lobby-text">Spielfeldgröße:</label>
                        <select
                            id="boardSize"
                            value={boardSize}
                            onChange={(e) => {
                                const newValue = e.target.value; // Den neuen Wert erfassen
                                socket.send("settings:size:" + newValue);
                            }}
                        >
                            <option value="5x5">5x5</option>
                            <option value="7x7">7x7</option>
                            <option value="9x9">9x9</option>
                        </select>
                    </div>

                    <div className="form-row">
                        <label htmlFor="privateLobby" className="lobby-text">Private Lobby:</label>
                        <input
                            id="privateLobby"
                            type="checkbox"
                            checked={privateLobby}
                            onChange={() => {
                                const newValue = !useStore.getState().privateLobby; // Neuer Wert ist das invertierte aktuelle privateLobby
                                socket.send("settings:privateLobby:" + (newValue ? "true" : "false")); // Nachricht an Backend senden
                            }}
                        />
                    </div>
                </div>

                {/* Teilnehmerliste */}
                <div className="lobby-participants">
                    <strong>Lobby Teilnehmer:</strong>
                    <ul className="lobby-list">
                        {players.map((player, index) => (
                            <li key={index} className="lobby-list-item">
                                {player.name}
                                {player.nummer !== 0 && ( // Nur für die Spieler kick funktion bereit stellen, welche eben nicht der host sind
                                    <button
                                        className="kick-button"
                                        onClick={() => handleKickPlayer(player.nummer)}
                                        title="Spieler entfernen"
                                    >
                                        ❌
                                    </button>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Lobby-Aktionen */}
                <div className="lobby-buttons">
                    <button className="button-elegante" onClick={createLobbyLink}>
                        Lobby-Link generieren
                    </button>
                    <button className="button-elegante" onClick={addAIPlayer}>
                        KI-Spieler hinzufügen
                    </button>
                </div>
                <div className="lobby-buttons">
                    <button className="button-elegante" onClick={startGame}>
                        Spiel starten
                    </button>
                </div>

                <div className="lobby-link-container">
                    {URL && (
                        <div>
                            <p className="lobby-link">
                                <a
                                    href="#"
                                    onClick={copyToClipboard}
                                >
                                    {URL}
                                </a>
                            </p>
                            {copied && <p className="copy-feedback">Kopiert!</p>}

                        </div>
                    )}
                </div>
            </div>
        );
    }


}

export default CreateLobby;

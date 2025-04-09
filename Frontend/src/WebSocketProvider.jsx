import React, {createContext, useContext, useEffect, useState} from "react";

// WebSocket Context erstellen
const WebSocketContext = createContext(null);
import useStore from "./StageManagement.jsx";
// Provider-Komponente
export const WebSocketProvider = ({children}) => {
    const [socket, setSocket] = useState(null);
    const setUID = useStore((state) => state.setUID);
    const setLOBBY = useStore((state) => state.setLOBBY_LIST);
    const setLOBBYLINK = useStore((state) => state.setLOBBYLINK);
    const setLOBBY_PARTICIPANTS = useStore((state) => state.setLOBBY_PARTICIPANTS);


    useEffect(() => {
        // Verbindung mit dem Websocket-Server herstellen
        const host = window.location.hostname;
        const path = `ws://${host}:8765/name`;
        const ws = new WebSocket(path);

        ws.onopen = () => {
            console.log("WebSocket verbunden");
        };

        ws.onmessage = (event) => {
            console.log("Nachricht vom Server:", event.data);
            try {
                var serverNachricht = JSON.parse(event.data);
                switch (serverNachricht.action) {
                    case "set_playername":
                        useStore.getState().setUID(serverNachricht.message.uid)
                        // setUID(serverNachricht.message.uid); //UID als String wird gespeichert
                        break;
                    case "lobbys":
                        setLOBBY(serverNachricht.message); //Lobby jSON objet für ViewLobbies
                        break;
                    case "create_lobby":
                        setLOBBYLINK(serverNachricht.message.link);//LOBBYLINK wird als string gespeichert
                        break;
                    case "join_lobby":
                        if (serverNachricht.status === "success") {
                            setLOBBY_PARTICIPANTS(serverNachricht.message);
                        } else {
                            console.error(`Error: ${serverNachricht.message}`);
                        }
                        break
                    case "get_lobby":
                        setLOBBY_PARTICIPANTS(serverNachricht.message);
                        break
                    case "start_game":
                        window.location.href = `http://${window.location.hostname}:5000/game/${useStore.getState().UID}`;
                        break
                    case "settings":
                        if (serverNachricht.status === "success") {
                            const {message} = serverNachricht;

                            // Größe des Spielfeldes aktualisieren
                            if (message.size) {
                                useStore.getState().setBoardSize(message.size);
                            }

                            // Private Lobby Status aktualisieren
                            if (message.privateLobby !== undefined) {
                                useStore.getState().setPrivateLobby(message.privateLobby === "true");
                            }

                            // Spieleranzahl aktualisieren
                            if (message.lobbysize) {
                                useStore.getState().setlobbysize(parseInt(message.lobbysize));
                            }
                        } else {
                            console.error(`Fehler beim Aktualisieren der Einstellungen: ${serverNachricht.message}`);
                        }
                        break;


                }
            } catch (error) {
                console.error("Fehler beim Parsen der Nachricht", error);
            }

        };

        ws.onerror = (error) => {
            console.error("WebSocket-Fehler:", error);
        };

        ws.onclose = () => {
            console.log("WebSocket-Verbindung geschlossen");
        };

        setSocket(ws);

        // Verbindung schließen, wenn der Provider entladen wird
        return () => ws.close();
    }, []);

    return (
        <WebSocketContext.Provider value={socket}>
            {children}
        </WebSocketContext.Provider>
    );
};

// Custom Hook für den Zugriff auf den WebSocket
export const useWebSocket = () => {
    return useContext(WebSocketContext);
};

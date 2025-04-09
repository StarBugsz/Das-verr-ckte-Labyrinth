import React, {useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import useStore from "../StageManagement.jsx";
import {useWebSocket} from "../WebSocketProvider.jsx";

function Menu() {
    const navigate = useNavigate();
    const socket = useWebSocket();

    const LOBBYLINK = useStore((state) => state.LOBBYLINK);
    const [waitingForLobby, setWaitingForLobby] = useState(false);

    //Kommunikation mit backend zur lobby erstellung
    const handleCreateLobby = () => {
        useStore.getState().setIsLobbyCreator(true);//Stellt sicher dass der Lobby creater die Host rechte bekommt
        socket.send("create_lobby");
        socket.send("get_lobby");
        setWaitingForLobby(true);//Zustandsvariable um zu wissen wann die lobby ready ist, um dann dort hin zu routen
    };
    //Warten bis lobby ready ist und routing zur lobby-Seite
    useEffect(() => {
        if (waitingForLobby && LOBBYLINK) {
            setWaitingForLobby(false);
            navigate(`/lobby/${LOBBYLINK}`);
        }
    }, [LOBBYLINK, waitingForLobby, navigate]);

    return (
        <div>
            <button
                className="button-elegante"
                onClick={handleCreateLobby}
                disabled={waitingForLobby}
            >
                {waitingForLobby ? "Lobby wird erstellt..." : "Lobby erstellen"}
            </button>
            <button
                className="button-elegante"
                onClick={() => {
                    useStore.getState().setIsLobbyCreator(false);
                    socket.send("lobbys");
                    navigate('/view-lobbies')
                }}
                disabled={waitingForLobby}
            >
                Lobbys anzeigen
            </button>
        </div>
    );
}

export default Menu;

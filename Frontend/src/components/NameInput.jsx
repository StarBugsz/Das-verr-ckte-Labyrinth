import React, {useEffect, useState} from 'react';
import '../index.css'
import useStore from "../StageManagement.jsx";
import {useWebSocket} from "../WebSocketProvider.jsx";
import {useNavigate} from "react-router-dom";


function NameInput() {
    const [name, setName] = useState('');
    const socket = useWebSocket();
    const navigate = useNavigate();

    const UID = useStore((state) => state.UID);
    const LOBBY_PARTICIPANTS = useStore((state) => state.LOBBY_PARTICIPANTS);
    const ComingFromLobby = useStore((state) => state.ComingFromLobby);
    const LOBBYLINK = useStore((state) => state.LOBBYLINK);

    //Name an backend übermitteln, mit test ob man ein komplett neuer Spieler ist,
    // oder gerade versucht über einen Joinlink einem spiel zu joinen. Um dann dementsprechend zu routen
    const handleSubmit = (e) => {
        e.preventDefault();
        socket.send("set_username:" + name);
        useStore.getState().setIsLobbyCreator(false);
        if (useStore.getState().ComingFromLobby) {
            socket.send("join_lobby:" + useStore.getState().LOBBYLINK);
        } else {
            navigate('/menu');
        }
    };

    useEffect(() => {
        if (ComingFromLobby && UID !== '' && Object.keys(LOBBY_PARTICIPANTS).length > 0) {
            navigate(`/lobby/${LOBBYLINK}`);
        }
    }, [UID, LOBBY_PARTICIPANTS, ComingFromLobby, LOBBYLINK, navigate]);

    return (
        <form className="form" onSubmit={handleSubmit}>
            <div className="input-group">
                <input required id="input" type="text" className="input" value={name}
                       onChange={(e) => setName(e.target.value)}/>
                <label className="user-label">
                    Username:
                </label>
            </div>
            <button className="button-elegante" type="submit">Weiter</button>
        </form>
    );
}

export default NameInput;

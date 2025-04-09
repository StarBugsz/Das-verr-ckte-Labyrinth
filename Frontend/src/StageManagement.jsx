import {create} from "zustand";
import {useState} from "react";

const useStore = create((set) => ({
    // Globale Variablen
    UID: '',
    LOBBY_LIST:{},
    LOBBYLINK: '',
    LOBBY_PARTICIPANTS:{},
    ComingFromLobby: false,
    IsLobbyCreator: false,

    lobbysize: 4,
    boardSize: "7x7",
    privateLobby: false,

    // Setter-Funktionen
    setUID: (newUID) => set({UID: newUID}),
    setLOBBY_LIST: (newLOBBY) => set({LOBBY_LIST: newLOBBY}),
    setLOBBYLINK: (newLOBBYLINK) => set({LOBBYLINK: newLOBBYLINK}),
    setLOBBY_PARTICIPANTS: (newLOBBYLINK) => set({LOBBY_PARTICIPANTS: newLOBBYLINK}),
    setComingFromLobby: (newComingFromLobby) => set({ComingFromLobby: newComingFromLobby}),
    setIsLobbyCreator:(newIsLobbyCreator) => set({IsLobbyCreator: newIsLobbyCreator}),

    setlobbysize: (newCount) => set({ lobbysize: newCount }),
    setBoardSize: (newSize) => set({ boardSize: newSize }),
    setPrivateLobby: (isPrivate) => set({ privateLobby: isPrivate }),
}));

export default useStore;
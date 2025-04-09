// src/App.jsx
import React, {useEffect, useState} from 'react';
import {BrowserRouter as Router, Route, Routes, useNavigate} from 'react-router-dom';
import NameInput from './components/NameInput';
import Menu from './components/Menu';
import CreateLobby from './components/CreateLobby';
import ViewLobbies from './components/ViewLobbies';
import {WebSocketProvider} from './WebSocketProvider';
import PageContainer from "./components/PageContainer.jsx";

function App() {
    return (
        <WebSocketProvider>
            <Router>
                <div className="App backGround">
                    <PageContainer>
                        <Routes>
                            <Route path="/" element={<NameInput/>}/>
                            <Route path="/menu" element={<Menu/>}/>
                            <Route path="/lobby/:lobbyId" element={<CreateLobby/>}/>
                            <Route path="/view-lobbies" element={<ViewLobbies/>}/>
                        </Routes>
                    </PageContainer>
                </div>
            </Router>
        </WebSocketProvider>
    );
}


export default App;

import { useState } from 'react'
import './App.css'
import Signup from './components/Signup/Signup'
import Login from './components/Login/Login';
import {BrowserRouter, Routes, Route } from "react-router-dom";
import Homepage from './components/Homepage/Homepage';

function App() {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleEmailChange = (value) => {
    return setEmail(value);
  }

  const handlePasswordChange = (value) => {
    return setPassword(value);
  }
  
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Signup email={email} password={password} handleEmailChange={handleEmailChange} handlePasswordChange={handlePasswordChange} />} />
          <Route path="/login" element={<Login email={email} password={password} handleEmailChange={handleEmailChange} handlePasswordChange={handlePasswordChange} />} />
          <Route path='/homepage' element={<Homepage/>}></Route>
        </Routes>
      </BrowserRouter>
    </>
  )
  
  
}

export default App

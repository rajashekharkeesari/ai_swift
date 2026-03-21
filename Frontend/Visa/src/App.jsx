import { useState } from 'react'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Home from './pages/Home'
import { Routes, Route, Navigate } from "react-router-dom"


function App() {
  const [loggedin, setLoggedin] = useState(false)

  return (
    <>

      <Routes>
        <Route path="/" element={loggedin ? <Home /> : <Navigate to="/Login" />}></Route>
        <Route path="/Login" element={<Login />}></Route>
        <Route path="/Signup" element={<Signup />}></Route>
      </Routes>

    </>


  )
}

export default App














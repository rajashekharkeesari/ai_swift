import React from 'react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
const Signup = ({ setLoggedin }) => {
    const [email, setEmail] = useState("")
    const [tel, setTel] = useState("")
    const [password, setPassword] = useState("")
    const navigate = useNavigate()

    const handleSignup = (e) => {
        e.preventDefault()
        setLoggedin(true)
        navigate("/")
    }

    return (
        <div className="flex items-center justify-center h-screen w-full bg-amber-300">

            <form
                onSubmit={handleSignup}
                className="flex flex-col gap-4 bg-white p-6 rounded-xl shadow-md w-80"
            >
                <h1 className="text-xl font-bold text-center">Signup</h1>

                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="p-2 border rounded"
                />

                <input
                    type="tel"
                    placeholder="Phone Number"
                    value={tel}
                    onChange={(e) => setTel(e.target.value)}
                    className="p-2 border rounded"
                />

                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="p-2 border rounded"
                />

                <button
                    type="submit"
                    className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
                >
                    Signup
                </button>
                <h3 className="text-sm text-center">
                    Already have account?{" "}
                    <Link to="/Login" className="text-blue-500 hover:underline">
                        Login
                    </Link>
                </h3>
            </form>
        </div>
    )
}

export default Signup
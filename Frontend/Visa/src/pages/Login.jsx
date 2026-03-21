import React, { useState } from 'react'
import { Link } from "react-router-dom"

const Login = () => {
    const [email, setEmail] = useState("")
    const [tel, setTel] = useState("")
    const [password, setPassword] = useState("")

    const handleLogin = (e) => {
        e.preventDefault()

        console.log("Email:", email)
        console.log("Phone:", tel)
        console.log("Password:", password)
    }

    return (
        <div className="flex items-center justify-center h-screen w-full bg-amber-300">

            <form
                onSubmit={handleLogin}
                className="flex flex-col gap-4 bg-white p-6 rounded-xl shadow-md w-80"
            >
                <h1 className="text-xl font-bold text-center">Login</h1>

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
                    Login
                </button>
                <h3 className="text-sm text-center">
                    No account?{" "}
                    <Link to="/Signup" className="text-blue-500 hover:underline">
                        Signup
                    </Link>
                </h3>
            </form>

        </div>
    )
}

export default Login
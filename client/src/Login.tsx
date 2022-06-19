import React, { FormEvent, MouseEvent, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "./components/Auth"

const inputClasses =
    "px-3 py-2 border border-gray-200 bg-white text-sm text-gray-800 rounded"

export function Login() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const auth = useAuth()
    const navigate = useNavigate()

    const handleClick = async (e: FormEvent) => {
        e.stopPropagation()
        e.preventDefault()
        setLoading(true)
        setError(null)
        try {
            await auth.login({ email, password })
            navigate("/")
        } catch (e: any) {
            setError(String(e))
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="bg-indigo-800 w-full h-full flex flex-col items-center justify-between">
            {/* spacer */}
            <div></div>
            <div className="bg-white shadow w-full max-w-sm rounded pt-2">
                <h1 className="text-center my-4 font-bold uppercase text-sm text-indigo-900">
                    Log In
                </h1>
                <form
                    className="flex flex-col space-y-4 p-3"
                    onSubmit={handleClick}
                >
                    <label
                        htmlFor="email"
                        aria-label="Email"
                        className="flex flex-col"
                    >
                        <input
                            type="email"
                            name="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Email"
                            className={inputClasses}
                        ></input>
                    </label>

                    <label
                        htmlFor="password"
                        aria-label="Password"
                        className="flex flex-col"
                    >
                        <input
                            type="password"
                            name="password"
                            required
                            value={password}
                            placeholder="Password"
                            onChange={(e) => setPassword(e.target.value)}
                            className={inputClasses}
                        ></input>
                    </label>

                    {error ? (
                        <div className="font-semibold text-red-600 text-sm">
                            {error}
                        </div>
                    ) : null}

                    <button
                        type="submit"
                        onClick={handleClick}
                        className="bg-indigo-500 text-white font-bold py-2"
                        disabled={loading}
                    >
                        {loading ? "Loading..." : "Log In"}
                    </button>
                </form>
            </div>
            <div className="w-full flex items-center justify-center text-indigo-100 text-xs py-2">
                Copyright &copy; Michael Helvey 2022
            </div>
        </div>
    )
}

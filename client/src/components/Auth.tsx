import React, { createContext, useCallback, useContext, useState } from "react"
import { Navigate, useLocation } from "react-router-dom"

const BASE_URL = "http://localhost:8000"

type LoginRequest = {
    email: string
    password: string
}

type User = {
    name: string
    email: string
}

type AuthContextType = {
    user: User | null
    login: (request: LoginRequest) => Promise<void>
    logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>(
    null as unknown as AuthContextType
)

/**
 * Get user for initializing state.  For now, because we can, just hardcode the
 * expiration, since we know the server expiration
 */
function initializeUser(): User | null {
    const user = localStorage.getItem("user")
    const expirationStr = localStorage.getItem("user_expiration")
    console.log("user: %o, expiration: %s", user, expirationStr)

    // if expiration string is out of date, does not exist, or if user doesn't
    // exist, clear everything and return null -- as far as we can tell, the
    // user isn't logged in
    if (new Date() > new Date(expirationStr as string) || !user) {
        return null
    }

    // otherwise, assume that the user is logged in and return it -- we can
    // always redirect to login later if we ever get a 401
    return JSON.parse(user) as User
}

export function AuthContextProvider({
    children,
}: React.PropsWithChildren<unknown>) {
    const [user, setUser] = useState<User | null>(initializeUser())

    const login = useCallback(
        async (request: LoginRequest) => {
            // get cookie:
            await fetch(`${BASE_URL}/accounts/login`, {
                credentials: "include",
                method: "POST",
                body: JSON.stringify(request),
                headers: { "Content-Type": "application/json" },
            })

            // get user json:
            const userResponse = await fetch(`${BASE_URL}/accounts/me`, {
                credentials: "include",
                headers: { "Content-Type": "application/json" },
            })
            if (userResponse.status === 401) {
                throw new Error(
                    "Invalid login token: could not fetch user from /accounts/me"
                )
            }
            const user = await userResponse.json()
            setUser(user)

            localStorage.setItem("user", JSON.stringify(user))
            const today = new Date()
            const tomorrow = new Date(today)
            tomorrow.setDate(tomorrow.getDate() + 1)
            localStorage.setItem("user_expiration", tomorrow.toISOString())
        },
        [setUser]
    )

    const logout = useCallback(async () => {
        await fetch(`${BASE_URL}/accounts/logout`, { method: "POST" })
        localStorage.removeItem("user")
        localStorage.removeItem("user_expiration")
        setUser(null)
    }, [setUser])

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth(): AuthContextType {
    return useContext(AuthContext)
}

export function RequireAuth({
    children,
}: React.PropsWithChildren<unknown>): React.ReactElement {
    const location = useLocation()
    const auth = useAuth()

    if (!auth.user) {
        return <Navigate to="/login" state={{ from: location }} replace />
    }

    return <>{children}</>
}

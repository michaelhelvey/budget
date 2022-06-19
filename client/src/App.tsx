import React, { Suspense } from "react"
import { ErrorBoundary } from "react-error-boundary"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import { AuthContextProvider, RequireAuth } from "./components/Auth"
import { Home } from "./components/Home"
import { Login } from "./Login"

function App() {
    return (
        <AuthContextProvider>
            <ErrorBoundary
                FallbackComponent={({ error }) => (
                    <div>
                        An error occurred while rendering the application:{" "}
                        {error.toString()}
                    </div>
                )}
            >
                <Suspense fallback={<div>Loading...</div>}>
                    <BrowserRouter>
                        <Routes>
                            <Route
                                path="/"
                                element={
                                    <RequireAuth>
                                        <Home />
                                    </RequireAuth>
                                }
                            />
                            <Route path="/login" element={<Login />} />
                        </Routes>
                    </BrowserRouter>
                </Suspense>
            </ErrorBoundary>
        </AuthContextProvider>
    )
}

export default App

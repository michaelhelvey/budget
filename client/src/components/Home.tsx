import React, { Suspense } from "react"
import { ErrorBoundary } from "react-error-boundary"
import { Link } from "react-router-dom"
import { useAuth } from "./Auth"
import { QueryClient, QueryClientProvider, useQuery } from "react-query"
import { getVariableCategories } from "../lib/api"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"

const queryClient = new QueryClient()

export function Home() {
    const auth = useAuth()
    return (
        <div className="bg-slate-50 w-full h-full">
            <nav className="py-3 px-6 flex justify-between items-center bg-white text-gray-800 text-sm font-semibold border-bottom border-gray-400 shadow">
                <Link to="/">Budget</Link>
                <button onClick={() => auth.logout()}>Log Out</button>
            </nav>
            <ErrorBoundary FallbackComponent={HomeError}>
                <Suspense fallback={<HomeLoading />}>
                    <QueryClientProvider client={queryClient}>
                        <div className="mt-8 mb-4">
                            <HomeTitle />
                        </div>
                        <div>
                            <NewTransactionForm />
                        </div>
                        <div className="px-4 my-6">
                            <div className="w-full border-b border-gray-600 px-4" />
                        </div>
                    </QueryClientProvider>
                </Suspense>
            </ErrorBoundary>
        </div>
    )
}

const now = new Date()
const month = new Intl.DateTimeFormat("en-US", { month: "long" }).format(now)
const year = now.getFullYear()
const dateString = now.toLocaleDateString()
// lol
const percentageDone = ((now.getDate() / 30) * 100).toFixed(0)

function HomeTitle() {
    return (
        <div className="flex justify-center items-center w-full space-x-6">
            <div className="font-bold text-2xl">
                {month} {year}
            </div>
            <div className="font-semibold text-base text-gray-600">
                {dateString} - {percentageDone}%
            </div>
        </div>
    )
}

function NewTransactionForm() {
    const { data: categories } = useQuery(
        "variable-categories",
        () => getVariableCategories(),
        { suspense: true }
    )
    return (
        <form className="flex flex-col px-3 space-y-4">
            <label htmlFor="category" aria-label="Category">
                <select
                    name="category"
                    className="w-full border border-gray-300 rounded bg-white text-sm font-bold p-4 text-gray-700"
                >
                    {categories?.map((c) => (
                        <option key={c}>{c}</option>
                    ))}
                </select>
            </label>
            <label htmlFor="amount" aria-label="Amount">
                <div className="rounded-full bg-white border border-gray-300 w-full px-4 py-3 font-bold text-xl flex items-center mb-4">
                    <FontAwesomeIcon
                        icon="dollar-sign"
                        className="text-gray-600"
                    />
                    <input
                        required
                        type="number"
                        step="0.1"
                        name="amount"
                        className="focus:outline-none"
                        style={{ width: "inherit" }}
                    ></input>
                    <button
                        type="submit"
                        className="rounded-full bg-blue-600 p-3 w-10 h-10 flex items-center justify-center"
                    >
                        <FontAwesomeIcon icon="plus" className="text-white" />
                    </button>
                </div>
            </label>
            <label htmlFor="title" aria-label="Title">
                <input
                    className="px-3 py-2 border border-gray-200 bg-white text-sm text-gray-800 rounded w-full"
                    name="title"
                    placeholder="Title"
                />
            </label>
            <label htmlFor="notes" aria-label="Notes">
                <textarea
                    className="px-3 py-2 border border-gray-200 bg-white text-sm text-gray-800 rounded w-full"
                    name="notes"
                    placeholder="Notes"
                />
            </label>
        </form>
    )
}

function HomeLoading() {
    return (
        <div className="p-4 flex items-center justify-center">Loading...</div>
    )
}

function HomeError({ error }: { error: Error }) {
    return (
        <div className="p-3">
            <div className="bg-white p-3 border border-gray-400 rounded">
                <div className="font-bold text-sm mb-2 text-red-600">
                    Error:
                </div>
                <pre className="whitespace-normal font-mono text-sm bg-slate-100 p-2 rounded">
                    {String(error)}
                </pre>
            </div>
        </div>
    )
}

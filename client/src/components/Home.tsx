import React, { FormEvent, Suspense, useState } from "react"
import { ErrorBoundary } from "react-error-boundary"
import { Link } from "react-router-dom"
import { useAuth } from "./Auth"
import { QueryClient, QueryClientProvider, useQuery } from "react-query"
import {
    getTransactionsSummary,
    getVariableCategories,
    MonthlyReport,
    saveNewTransaction,
} from "../lib/api"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"

const queryClient = new QueryClient()

export function Home() {
    const auth = useAuth()
    // silly, stupid hack to update a child component whenever a callback is called
    const [queryKey, setQueryKey] = useState(0)
    const update = () => setQueryKey((k) => k + 1)

    return (
        <div className="bg-slate-50 w-full h-full pb-4 flex flex-col items-center">
            <nav className="py-3 px-6 flex justify-between items-center bg-white text-gray-800 text-sm font-semibold border-bottom border-gray-400 shadow w-full">
                <Link to="/">Budget</Link>
                <button onClick={() => auth.logout()}>Log Out</button>
            </nav>
            <ErrorBoundary FallbackComponent={HomeError}>
                <Suspense fallback={<HomeLoading />}>
                    <QueryClientProvider client={queryClient}>
                        <div className="w-full max-w-md">
                            <div className="mt-8 mb-4">
                                <HomeTitle />
                            </div>
                            <div>
                                <NewTransactionForm updateParent={update} />
                            </div>
                            <div className="px-4 my-6">
                                <div className="w-full border-b border-gray-600 px-4" />
                            </div>
                            <div>
                                <TransactionsSummary queryKey={queryKey} />
                            </div>
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

function NewTransactionForm({ updateParent }: { updateParent: () => void }) {
    const { data: categories } = useQuery(
        "variable-categories",
        () => getVariableCategories(),
        { suspense: true }
    )

    const [loading, setLoading] = useState(false)
    const [category, setCategory] = useState(categories![0])
    const [amount, setAmount] = useState("")
    const [title, setTitle] = useState("")
    const [notes, setNotes] = useState("")

    const handleFormSubmit = async (e: FormEvent) => {
        e.preventDefault()
        const payload = {
            category,
            amount: Number(amount),
            title,
            notes,
        }

        setLoading(true)
        await saveNewTransaction(payload)
        // yay, react 18
        setLoading(false)
        setCategory(categories![0])
        setAmount("")
        setTitle("")
        setNotes("")

        updateParent()
    }

    return (
        <form
            className="flex flex-col px-3 space-y-4"
            onSubmit={handleFormSubmit}
        >
            <label htmlFor="category" aria-label="Category">
                <select
                    name="category"
                    value={category}
                    onChange={(e) =>
                        setCategory(categories![e.target.selectedIndex])
                    }
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
                        name="amount"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                        className="focus:outline-none pl-4"
                        style={{ width: "inherit" }}
                    ></input>
                    <button
                        type="submit"
                        disabled={loading}
                        className="rounded-full bg-blue-600 p-3 w-10 h-10 flex items-center justify-center"
                    >
                        {!loading ? (
                            <FontAwesomeIcon
                                icon="plus"
                                className="text-white"
                            />
                        ) : (
                            "..."
                        )}
                    </button>
                </div>
            </label>
            <label htmlFor="title" aria-label="Title">
                <input
                    className="px-3 py-2 border border-gray-200 bg-white text-sm text-gray-800 rounded w-full"
                    name="title"
                    placeholder="Title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                />
            </label>
            <label htmlFor="notes" aria-label="Notes">
                <textarea
                    className="px-3 py-2 border border-gray-200 bg-white text-sm text-gray-800 rounded w-full"
                    name="notes"
                    placeholder="Notes"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value.trim())}
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

function formatDollar(cents: number) {
    return (cents / 100).toFixed(2)
}

function TransactionsSummary({ queryKey }: { queryKey: number }) {
    const { data: response } = useQuery(
        ["transactions-summary", queryKey],
        () => getTransactionsSummary(),
        { suspense: true }
    )
    // Safety: suspense
    const data = response as MonthlyReport

    return (
        <div className="px-4 space-y-4">
            <div className="w-full bg-white border border-gray-300 px-3 py-2 rounded text-sm text-gray-600 text-center">
                <span className="font-bold text-black mr-1">
                    ${formatDollar(data.totals.spent)}
                </span>
                spent of ${formatDollar(data.totals.unallocated)} unallocated
            </div>
            {Object.values(data.categories).map((category) => (
                <CategoryDropDown category={category} key={category.category} />
            ))}
        </div>
    )
}

type CategoryDropDownProps = {
    category: MonthlyReport["categories"][1]
}

function CategoryDropDown({ category }: CategoryDropDownProps) {
    const [open, setOpen] = useState(false)

    return (
        <button
            className="bg-white shadow rounded w-full"
            onClick={() => setOpen((o) => !o)}
        >
            <div className="flex items-center p-6">
                <FontAwesomeIcon icon={["fas", "bag-shopping"]} />
                <div className="block flex-1 px-8 text-left">
                    <div className="text-sm text-gray-700 font-semibold">
                        {category.category}
                    </div>
                    <div className="mt-2">
                        <span className="text-lg font-bold">
                            ${formatDollar(category.total)}
                        </span>
                        <span
                            className={`font-bold ml-2 ${
                                category.vs_previous_month > 0
                                    ? "text-red-600"
                                    : "text-green-600"
                            }`}
                        >
                            {category.vs_previous_month ? (
                                <>
                                    {category.vs_previous_month > 0 ? "+" : ""}
                                    {category.vs_previous_month.toFixed(2)}%
                                </>
                            ) : null}
                        </span>
                    </div>
                </div>
                <FontAwesomeIcon
                    icon={open ? "chevron-down" : "chevron-right"}
                />
            </div>
            {open ? (
                <div className="border-t border-gray-300">
                    {category.transactions.map((transaction) => (
                        <CategoryTransaction
                            key={transaction.created_at}
                            transaction={transaction}
                        />
                    ))}
                </div>
            ) : null}
        </button>
    )
}

type CategoryTransactionProps = {
    transaction: MonthlyReport["categories"][1]["transactions"][0]
}

function transactionDateFormat(dt: string): string {
    const date = new Date(dt)
    const month = date.getMonth() + 1
    const day = date.getDate()

    const monthStr = month < 10 ? `0${month}` : String(month)
    const dayStr = day < 10 ? `0${day}` : String(day)

    return `${monthStr}/${dayStr}`
}

function CategoryTransaction({ transaction }: CategoryTransactionProps) {
    return (
        <div className="p-3 text-xs flex items-center">
            <div className="text-gray-700">
                {transactionDateFormat(transaction.created_at)}
            </div>
            <div className="block pl-6 text-left flex-1">
                <div className="font-bold text-gray-800">
                    {transaction.title ?? "No Title"}
                </div>
                <div className="text-gray-600 mt-2">
                    {transaction.notes ?? "No Notes"}
                </div>
            </div>
            <div className="font-bold text-base pr-2">
                ${formatDollar(transaction.amount)}
            </div>
        </div>
    )
}

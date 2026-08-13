import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import axios from 'axios';
import { Sparkles, UserPlus } from "lucide-react";

import api from "../../api/api.js";

function Signup() {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (formData.password !== formData.confirmPassword) {
            alert("Passwords do not match");
            return;
        }

        try {
            const response = await api.post("/auth/signup", {
                username: formData.username,
                email: formData.email,
                password: formData.password,
            });

            console.log(response.data);
            alert("Signup successful! Please verify your email.");
            navigate("/login");
        }

        catch (err) {
            console.log(err);

            if (err.response) {
                console.log(err.response.data);
            } else {
                console.log(err.message);
            }
            
            alert("Signup failed. Please try again.");
        }
    };

    return (
        <div className="flex min-h-[calc(100vh-64px)] items-center justify-center bg-zinc-50 px-4 py-12 dark:bg-zinc-950">
            <div className="w-full max-w-md rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">

                <div className="mb-6 flex flex-col items-center text-center">
                    <span className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600 text-white">
                        <Sparkles size={20} strokeWidth={2.25} />
                    </span>
                    <h1 className="font-display text-2xl font-bold text-zinc-900 dark:text-white">
                        Create your account
                    </h1>
                    <p className="mt-1.5 text-sm text-zinc-500 dark:text-zinc-400">
                        Start chatting with your documents in minutes.
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">

                    <input
                        type="text"
                        name="username"
                        placeholder="Username"
                        value={formData.username}
                        onChange={handleChange}
                        className="focus-ring w-full rounded-lg border border-zinc-300 bg-white p-3 text-sm text-zinc-900 outline-none transition-colors placeholder:text-zinc-400 focus:border-indigo-500 dark:border-zinc-700 dark:bg-zinc-950 dark:text-white dark:placeholder:text-zinc-500 dark:focus:border-indigo-400"
                        required
                    />

                    <input
                        type="email"
                        name="email"
                        placeholder="Email"
                        value={formData.email}
                        onChange={handleChange}
                        className="focus-ring w-full rounded-lg border border-zinc-300 bg-white p-3 text-sm text-zinc-900 outline-none transition-colors placeholder:text-zinc-400 focus:border-indigo-500 dark:border-zinc-700 dark:bg-zinc-950 dark:text-white dark:placeholder:text-zinc-500 dark:focus:border-indigo-400"
                        required
                    />

                    <input
                        type="password"
                        name="password"
                        placeholder="Password"
                        value={formData.password}
                        onChange={handleChange}
                        className="focus-ring w-full rounded-lg border border-zinc-300 bg-white p-3 text-sm text-zinc-900 outline-none transition-colors placeholder:text-zinc-400 focus:border-indigo-500 dark:border-zinc-700 dark:bg-zinc-950 dark:text-white dark:placeholder:text-zinc-500 dark:focus:border-indigo-400"
                        required
                    />

                    <input
                        type="password"
                        name="confirmPassword"
                        placeholder="Confirm Password"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        className="focus-ring w-full rounded-lg border border-zinc-300 bg-white p-3 text-sm text-zinc-900 outline-none transition-colors placeholder:text-zinc-400 focus:border-indigo-500 dark:border-zinc-700 dark:bg-zinc-950 dark:text-white dark:placeholder:text-zinc-500 dark:focus:border-indigo-400"
                        required
                    />

                    <button
                        type="submit"
                        className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-indigo-600 py-3 font-semibold text-white shadow-sm transition-colors hover:bg-indigo-700"
                    >
                        <UserPlus size={17} strokeWidth={2.25} />
                        Sign Up
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-zinc-500 dark:text-zinc-400">
                    Already have an account?{" "}
                    <Link
                        to="/login"
                        className="font-semibold text-indigo-600 hover:underline dark:text-indigo-400"
                    >
                        Login
                    </Link>
                </p>
            </div>
        </div>
    );
}

export default Signup;
import { Logo } from "@/components/sidebar/Logo";
import { enterApp } from "./actions";

export default function Page() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-page px-6">
      <div className="w-full max-w-md rounded-2xl border border-line bg-white p-10 text-center shadow-sm">
        <div className="flex justify-center">
          <Logo className="h-11 w-auto" />
        </div>
        <h1 className="mt-6 text-2xl font-bold tracking-tight text-ink">
          Welcome to Dailoqa
        </h1>
        <p className="mt-2 text-sm text-ink-soft">
          Choose how you want to enter the console.
        </p>

        <div className="mt-8 flex flex-col gap-3">
          <form action={enterApp.bind(null, "user")}>
            <button
              type="submit"
              className="w-full rounded-lg bg-accent px-5 py-3 text-sm font-semibold text-white transition-colors hover:opacity-90"
            >
              User
            </button>
          </form>
          <form action={enterApp.bind(null, "admin")}>
            <button
              type="submit"
              className="w-full rounded-lg border border-line bg-white px-5 py-3 text-sm font-semibold text-ink transition-colors hover:bg-hover"
            >
              Admin
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}

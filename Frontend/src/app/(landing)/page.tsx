import { redirect } from "next/navigation";
import { Logo } from "@/shared/ui";
import { SignInButton, getSession } from "@/features/auth";

export default async function Page() {
  if (await getSession()) redirect("/dashboard");

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
          Sign in to enter the console.
        </p>

        <div className="mt-8">
          <SignInButton />
        </div>
      </div>
    </main>
  );
}

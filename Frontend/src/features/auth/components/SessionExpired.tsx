import { Logo } from "@/shared/ui";

export function SessionExpired() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-page px-6">
      <div className="w-full max-w-md rounded-2xl border border-line bg-white p-10 text-center shadow-sm">
        <div className="flex justify-center">
          <Logo className="h-11 w-auto" />
        </div>
        <h1 className="mt-6 text-2xl font-bold tracking-tight text-ink">Your session has ended</h1>
        <p className="mt-2 text-sm text-ink-soft">
          You were signed out, so this conversation is no longer available here.
        </p>
      </div>
    </main>
  );
}

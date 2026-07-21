export type StartingPoint = {
  image: string;
  title: string;
  description: string;
  href: string;
};

export const startingPoints: StartingPoint[] = [
  {
    image: "/DeepAgent.jpg",
    title: "Deep Agents",
    description:
      "Build agents for complex, long-running tasks. A complete agent harness with planning, subagents, a virtual filesystem, and long-term memory built in. The fastest way to start.",
    href: "/docs/deepagents",
  },
  {
    image: "/LangChain.jpg",
    title: "LangChain",
    description:
      "A minimal, configurable agent framework. Compose exactly what you need from models, tools, prompts, and middleware.",
    href: "/docs/langchain",
  },
  {
    image: "/LangGraph.jpg",
    title: "LangGraph",
    description:
      "Low-level orchestration for stateful, long-running agents: durable execution, streaming, memory, and human-in-the-loop.",
    href: "/docs/langgraph",
  },
];

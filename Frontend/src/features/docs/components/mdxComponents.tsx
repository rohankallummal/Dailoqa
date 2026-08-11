import type { ComponentProps } from "react";
import { compileSnippets } from "../lib/snippets";
import { LangBlock } from "./LangBlock";
import { CodeBlock } from "./CodeBlock";
import { CodeGroup } from "./CodeGroup";
import { Card } from "./Card";
import { AccordionGroup, CardGroup, Grid } from "./Grid";
import { Accordion } from "./Accordion";
import { Expandable } from "./Expandable";
import { Callout, Note, Tip, Warning } from "./Callout";
import { Icon } from "./Icon";
import { ParamField } from "./ParamField";
import { Tab, Tabs } from "./Tabs";
import { Tooltip } from "./Tooltip";
import { Frame } from "./Frame";
import { Step, Steps } from "./Steps";
import { Tree } from "./Tree";
import { MdxLink } from "./MdxLink";

type Components = Record<string, unknown>;

const shims: Components = {
  LangBlock,
  CodeBlock,
  CodeGroup,
  Card,
  CardGroup,
  Columns: Grid,
  Accordion,
  AccordionGroup,
  Expandable,
  Note,
  Info: Note,
  Tip,
  Warning,
  Callout,
  ParamField,
  Tabs,
  Tab,
  Tooltip,
  Frame,
  Steps,
  Step,
  Tree,
  Icon,
  a: MdxLink,
};

let cache: Components | null = null;

export async function getMdxComponents(): Promise<Components> {
  if (cache) return cache;
  const snippets = await compileSnippets();
  const components: Components = { ...shims };
  for (const [name, Snippet] of Object.entries(snippets)) {
    components[name] = (props: ComponentProps<typeof Snippet>) => (
      <Snippet {...props} components={components} />
    );
  }
  cache = components;
  return components;
}

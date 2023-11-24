import matchers from "@testing-library/jest-dom/matchers";
import { expect } from "vitest";

expect.extend(matchers); //* Add in Jest-Dom matchers to the normal ones

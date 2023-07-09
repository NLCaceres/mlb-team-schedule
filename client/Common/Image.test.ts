import Image from "./Image.svelte";
import { render, screen, fireEvent } from "@testing-library/svelte";

describe("renders an image that renders a placeholder if the URL doesn't load", () => {
  describe("rendering a placeholder", () => {
    test("if no 'source' URL is passed in", () => {
      const { rerender } = render(Image, { source: "", altText: "Foobar" });
      expect(screen.queryByRole("img")).not.toBeInTheDocument();
      expect(screen.getByText("Missing Foobar")).toBeInTheDocument(); //* Uses the alt text in the placeholder
  
      rerender({ source: "some_url.jpg", altText: "Foobar" });
      const img = screen.getByRole("img");
      expect(img).toBeInTheDocument();
      expect(img).toHaveAttribute("src", "some_url.jpg");
      expect(img).toHaveAttribute("alt", "Foobar"); //* Alt text prop inserted
    })
    test("if the img fails to load properly", async () => {
      render(Image, { source: "img.jpg", altText: "Foobar" });
      const img = screen.getByRole("img");
      expect(img).toBeInTheDocument();
      
      await fireEvent.error(img); //* Simulate the img load failing and throwing an error
      expect(img).not.toBeInTheDocument(); //* Which sets the hasError prop
      expect(screen.getByText(/missing/i)).toBeInTheDocument(); //* Rendering in the placeholder instead!
    })
  })

  describe("uses props to handle CSS styling", () => {
    test("uses height and width props to handle img aspect ratio", () => {
      const { rerender } = render(Image, { source: "foo.jpg", height: 20, width: 20 });
      const img = screen.getByRole("img");
      expect(img).toBeInTheDocument();
      expect(img).toHaveStyle("height: 20px; width: 20px;");

      rerender({ source: "foo.jpg", height: 0, width: 0 });
      const zeroImg = screen.getByRole("img");
      expect(zeroImg).toBeInTheDocument();
      //* Deliberately passing in 0 creates an empty style string to avoid an invisible img
      expect(zeroImg).toHaveAttribute("style", " ");
    })
    test("has an optional miniature size based on 'miniView' prop", () => {
      const { rerender } = render(Image, { source: "foo.jpg", miniView: true });
      const img = screen.getByRole("img");
      expect(img).toBeInTheDocument();
      expect(img).toHaveClass("miniView");

      rerender({ source: "foo.jpg", miniView: false });
      const rerenderedImg = screen.getByRole("img")
      expect(rerenderedImg).toBeInTheDocument();
      expect(rerenderedImg).not.toHaveClass("miniView");
    })
    test("dynamically adding in styling for the placeholder", () => {
      const { rerender } = render(Image, { placeholderStyleString: "height: 20px;" });
      expect(screen.getByText(/missing/i)).toHaveStyle("height: 20px;");

      rerender({ placeholderStyleString: "width: 20px; "});
      expect(screen.getByText(/missing/i)).toHaveStyle("width: 20px;");
    })
  })
})
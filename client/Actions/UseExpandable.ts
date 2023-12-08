//? Since Svelte Transitions (like Vue Transitions) are meant to move DOM elements in and out
//? AND since Svelte Animations are limited to the keyed children of an {#each} block,
//? Svelte Actions are left as the logical choice to make a reusable animation (rather than using afterUpdate() to call this animation)
//? Any function that has an Element as its 1st arg, and a prop as its 2nd, can be an action
//? The prop arg can be an object if multiple props are needed
export function expandable(node: HTMLElement, willExpand: boolean) { // eslint-disable-line @typescript-eslint/no-unused-vars
  const initialHeight = node.offsetHeight;
  const heightVals: [number, number] = [initialHeight, 0];
  let firstUpdate = true;
  return { //? May return an update and destroy func. The update is called EVERY time the component updates the props of the prop arg
    update(isExpanded: boolean) { //? Sometimes a prop arg is only needed/used in the update() return func
      if (firstUpdate) { heightVals[1] = node.offsetHeight; firstUpdate = false; }

      const animation = node.animate([{ height: `${heightVals[0]}px` }, { height: `${heightVals[1]}px` }], { duration: 500, easing: "ease" });
      animation.pause(); //* Prevents the animation from immediately starting
      (isExpanded) ? animation.play() : animation.reverse();
    }
  };
}

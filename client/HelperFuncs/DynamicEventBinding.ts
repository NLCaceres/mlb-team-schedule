//? Idea here is to create Vue-like dynamic event handler directive <div @['dynamicEventName']></div>
//* Usage: <div use:bindEvents={{eventName: eventHandlerFunction}, {eventName2: eventHandlerFunction2}, {eventName3: eventHandlerFunction}}></div>
//* The bonus here is that you set multiple dynamic names!
type eventObj = Record<string, EventListenerOrEventListenerObject>;
export default function bindEvents(node: Element, events: eventObj) {

  const listeners = Object.entries(events).map(([eventName, eventHandler]) => {
    node.addEventListener(eventName, eventHandler);
    return [eventName, eventHandler];
  });

  return {
    destroy() {
      listeners.forEach(([eventName, eventHandler]) => {
        node.removeEventListener(eventName as string, eventHandler as EventListenerOrEventListenerObject);
      });
    }
  };
}
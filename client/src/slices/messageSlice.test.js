// src/slices/messageSlice.test.js
import { messageReducer, setMessage, clearMessage } from "./messageSlice";

describe("messageSlice", () => {
  it("should return the initial state", () => {
    const initialState = { message: "" };
    expect(messageReducer(undefined, {})).toEqual(initialState);
  });

  it("should set a message", () => {
    const previousState = { message: "" };
    const newMessage = "Test message";

    const newState = messageReducer(previousState, setMessage(newMessage));

    expect(newState).toEqual({ message: newMessage });
  });

  it("should clear the message", () => {
    const previousState = { message: "This is a message" };

    const newState = messageReducer(previousState, clearMessage());

    expect(newState).toEqual({ message: "" });
  });
});

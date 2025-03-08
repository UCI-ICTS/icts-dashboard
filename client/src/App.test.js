import React from "react";
import { screen } from "@testing-library/react";
import { renderWithProviders } from "./test-utils";
import App from "./App";

test("renders learn react link", () => {
  renderWithProviders(<App />, {
    preloadedState: { account: { isLoggedIn: true, user: { username: "testUser" }, loading: false } },
    withRouter: false, // 🚀 Don't wrap with another Router
  });

  expect(screen.getByText(/UCI ICTS Dashboard/i)).toBeInTheDocument();
});

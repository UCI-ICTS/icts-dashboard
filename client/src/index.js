import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import App from './App';
import { message } from 'antd'; // ← Import message from antd
import { GoogleOAuthProvider } from '@react-oauth/google';

// Set global message duration (in seconds)
message.config({
  duration: 5, // e.g. show messages for 5 seconds instead of 2
});
const GOOGLE_CLIENT_ID="707343581069-oe3rocjvd5cjvb1jaajjtict9pofeql7.apps.googleusercontent.com"
console.log("client_id:", GOOGLE_CLIENT_ID);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <Provider store={store}>
        <BrowserRouter>
            <App />
        </BrowserRouter>
      </Provider>
    </GoogleOAuthProvider>
  </React.StrictMode>
);
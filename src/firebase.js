import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyCsBsbVsTa-P0VH9KVqyDvLbkM7-9zJ0Uk",
  authDomain: "web-app-97424.firebaseapp.com",
  projectId: "web-app-97424",
  storageBucket: "web-app-97424.firebasestorage.app",
  messagingSenderId: "382701463670",
  appId: "1:382701463670:web:cd56fde5a132ceed60d757",
  measurementId: "G-2KK5H1Y4EJ"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const googleprovider = new GoogleAuthProvider();

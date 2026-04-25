import { createBrowserRouter } from "react-router";
import { MonitorView } from "./components/MonitorView";
import { LoginDialog } from "./components/LoginDialog";
import { useState } from "react";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
  },
]);

function Root() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showLoginDialog, setShowLoginDialog] = useState(false);

  const handleLogin = (passcode: string) => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  return (
    <div className="h-screen w-screen bg-gray-50 text-gray-900 flex flex-col">
      <main className="flex-1 overflow-hidden">
        <MonitorView 
          onLogout={isLoggedIn ? handleLogout : undefined} 
          isLoggedIn={isLoggedIn}
          onLoginClick={() => setShowLoginDialog(true)}
        />
      </main>

      {/* 登录弹框 */}
      <LoginDialog
        open={showLoginDialog}
        onClose={() => setShowLoginDialog(false)}
        onLogin={handleLogin}
      />
    </div>
  );
}
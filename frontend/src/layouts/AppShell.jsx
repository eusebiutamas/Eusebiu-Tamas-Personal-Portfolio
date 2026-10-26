import { Outlet } from 'react-router-dom';

function AppShell() {
  return (
    <main 
      className="page-content"
      style={{ 
        paddingTop: '120px',
        paddingBottom: '40px',
        minHeight: '100vh',
        position: 'relative',
        zIndex: 10
      }}
    >
      <Outlet />
    </main>
  );
}

export default AppShell;
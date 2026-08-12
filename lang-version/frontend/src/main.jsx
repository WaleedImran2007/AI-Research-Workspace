import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AuthProvider } from '../Context/AuthContext.jsx';

// COMPONENTS
import Home from './pages/Home.jsx';
import SignUp from './pages/SignUp.jsx';
import Login from './pages/Login.jsx';
import Collections from './pages/Collections.jsx';
import CollectionDetails from './pages/CollectionDetails.jsx';
import AI from './pages/AI.jsx';
import PDFViewer from './pages/PDFViewer.jsx';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <Home /> },
      { path: '/signup', element: <SignUp /> },
      { path: '/login', element: <Login /> },
      { path: '/collections', element: <Collections /> },
      { path: '/collections/:collectionId', element: <CollectionDetails /> },
      { path: '/ai', element: <AI /> },
      { path: '/documents/:documentId', element: <PDFViewer /> }
    ]
  }

])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </StrictMode>,
)
